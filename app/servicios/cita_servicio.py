# ¿De dónde sale cada método?
# reservar()            → RF-06 el paciente reserva por link público
# obtener_por_token()   → RF-06 el paciente consulta su cita
# listar_por_prof()     → RF-08 el profesional ve su agenda
# cancelar()            → RF-08 cancelar cita
# reagendar()           → RF-08 solo el profesional reagenda
# marcar_asistencia()   → RF-08 marcar si vino o no
# agregar_nota()        → RF-08 nota clínica privada
# slots_disponibles()   → RF-06 calendario público

from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import secrets
from app.modelos.cita_modelo import Cita
from app.modelos.paciente_modelo import Paciente
from app.modelos.nota_cita_modelo import NotaCita
from app.modelos.profesional_modelo import Profesional
from app.esquemas.cita_esquema import (
    ReservarCitaEntrada, CancelarCitaEntrada,
    ReagendarCitaEntrada, MarcarAsistenciaEntrada,
    NotaCitaEntrada, SlotDisponibleSalida,
)
from app.core.excepciones import (
    NoEncontradoExcepcion, HorarioNoDisponibleExcepcion,
    SolicitudInvalidaExcepcion,
)



ESTADOS_ACTIVOS = ["pendiente", "confirmada"]


class CitaServicio:

    def __init__(self, db: Session):
        self.db = db

    def _verificar_slot_libre(self, profesional_id: int, inicio: datetime, fin: datetime, excluir_id: int = None):
        """Verifica que no haya otra cita en ese horario."""
        query = self.db.query(Cita).filter(
            Cita.profesional_id == profesional_id,
            Cita.estado.in_(ESTADOS_ACTIVOS),
            Cita.inicio < fin,
            Cita.fin > inicio,
        )
        if excluir_id:
            query = query.filter(Cita.id != excluir_id)
        if query.first():
            raise HorarioNoDisponibleExcepcion()

    def reservar(self, profesional: Profesional, datos: ReservarCitaEntrada) -> Cita:
        fin = datos.inicio + timedelta(minutes=profesional.duracion_cita_min)
        self._verificar_slot_libre(profesional.id, datos.inicio, fin)

        try:
            # Buscar paciente por teléfono o crear uno nuevo
            paciente = self.db.query(Paciente).filter(
                Paciente.telefono == datos.telefono_paciente,
                Paciente.organizacion_id == profesional.organizacion_id,
                Paciente.eliminado_en == None,
            ).first()

            if not paciente:
                paciente = Paciente(
                    organizacion_id=profesional.organizacion_id,
                    nombre_completo=datos.nombre_paciente,
                    telefono=datos.telefono_paciente,
                    email=datos.email_paciente,
                )
                self.db.add(paciente)
                self.db.flush()

            estado_inicial = "pendiente" if profesional.requiere_pago else "confirmada"

            cita = Cita(
                profesional_id=profesional.id,
                paciente_id=paciente.id,
                organizacion_id=profesional.organizacion_id,
                inicio=datos.inicio,
                fin=fin,
                estado=estado_inicial,
                motivo=datos.motivo,
                token_reserva=secrets.token_hex(32),
            )
            self.db.add(cita)
            self.db.commit()
            self.db.refresh(cita)

            # ── Notificaciones ────────────────────────────────────
            from app.servicios.notificacion_servicio import NotificacionServicio
            notif_svc = NotificacionServicio(self.db)
            # 1. Confirmación inmediata al paciente
            notif_svc.enviar_confirmacion(
                cita=cita,
                nombre_paciente=paciente.nombre_completo,
                nombre_profesional=profesional.nombre_completo,
                telefono=paciente.telefono,
            )
            # 2. Aviso al profesional si tiene teléfono
            if profesional.telefono:
                notif_svc.notificar_profesional_nueva_cita(
                    cita=cita,
                    nombre_paciente=paciente.nombre_completo,
                    nombre_profesional=profesional.nombre_completo,
                    telefono_profesional=profesional.telefono,
                )

            return cita

        except Exception:
            self.db.rollback()
            raise

    def obtener_por_token(self, token: str) -> Cita:
        cita = self.db.query(Cita).filter(Cita.token_reserva == token).first()
        if not cita:
            raise NoEncontradoExcepcion("Cita no encontrada")
        return cita

    def obtener_por_id(self, cita_id: int, organizacion_id: int) -> Cita:
        cita = self.db.query(Cita).filter(
            Cita.id == cita_id,
            Cita.organizacion_id == organizacion_id,
        ).first()
        if not cita:
            raise NoEncontradoExcepcion("Cita no encontrada")
        return cita

    def listar_por_profesional(self, profesional_id: int, organizacion_id: int,
                                estado: str = None, fecha_desde: datetime = None,
                                fecha_hasta: datetime = None):
        query = self.db.query(Cita).filter(
            Cita.profesional_id == profesional_id,
            Cita.organizacion_id == organizacion_id,
        )
        if estado:
            query = query.filter(Cita.estado == estado)
        if fecha_desde:
            query = query.filter(Cita.inicio >= fecha_desde)
        if fecha_hasta:
            query = query.filter(Cita.inicio <= fecha_hasta)
        return query.order_by(Cita.inicio).all()

    def cancelar(self, cita: Cita, datos: CancelarCitaEntrada) -> Cita:
        if cita.estado not in ESTADOS_ACTIVOS:
            raise SolicitudInvalidaExcepcion(
                f"No se puede cancelar una cita en estado '{cita.estado}'"
            )
        cita.estado = "cancelada"
        cita.motivo_cancelacion = datos.motivo_cancelacion
        self.db.flush()
        # ── Notificaciones ────────────────────────────────
        from app.servicios.notificacion_servicio import NotificacionServicio
        from app.modelos.paciente_modelo import Paciente
        from app.modelos.profesional_modelo import Profesional
        paciente    = self.db.query(Paciente).filter(Paciente.id == cita.paciente_id).first()
        profesional = self.db.query(Profesional).filter(Profesional.id == cita.profesional_id).first()
        notif_svc   = NotificacionServicio(self.db)
        # Avisa al paciente
        if paciente:
            notif_svc.enviar_cancelacion_paciente(
                cita=cita,
                nombre_paciente=paciente.nombre_completo,
                nombre_profesional=profesional.nombre_completo,
                telefono=paciente.telefono,
            )
        # Avisa al profesional
        if profesional and profesional.telefono:
            notif_svc.notificar_profesional_cancelacion(
                cita=cita,
                nombre_paciente=paciente.nombre_completo,
                nombre_profesional=profesional.nombre_completo,
                telefono_profesional=profesional.telefono,
            )
        self.db.commit()
        self.db.refresh(cita)
        return cita

    def reagendar(self, cita: Cita, profesional: Profesional, datos: ReagendarCitaEntrada) -> Cita:
        if cita.estado not in ESTADOS_ACTIVOS:
            raise SolicitudInvalidaExcepcion(f"No se puede reagendar una cita en estado '{cita.estado}'")
        nuevo_fin = datos.nuevo_inicio + timedelta(minutes=profesional.duracion_cita_min)
        self._verificar_slot_libre(profesional.id, datos.nuevo_inicio, nuevo_fin, excluir_id=cita.id)
        cita.inicio = datos.nuevo_inicio
        cita.fin = nuevo_fin
        self.db.commit()
        self.db.refresh(cita)
        return cita

    def marcar_asistencia(self, cita: Cita, datos: MarcarAsistenciaEntrada) -> Cita:
        cita.asistio = datos.asistio
        cita.estado = "completada" if datos.asistio else "no_asistio"
        self.db.commit()
        self.db.refresh(cita)
        return cita

    def agregar_nota(self, cita: Cita, profesional_id: int, datos: NotaCitaEntrada) -> NotaCita:
        nota = NotaCita(
            cita_id=cita.id,
            profesional_id=profesional_id,
            contenido=datos.contenido,
            es_privada=datos.es_privada,
        )
        self.db.add(nota)
        self.db.commit()
        self.db.refresh(nota)
        return nota

    def slots_disponibles(self, profesional: Profesional, fecha: datetime):
        dia_semana = fecha.weekday()
        horario = next(
            (h for h in profesional.horarios if h.dia_semana == dia_semana and h.esta_activo),
            None
        )
        if not horario:
            return []

        slots = []
        inicio = datetime.combine(fecha.date(), horario.hora_inicio)
        fin_dia = datetime.combine(fecha.date(), horario.hora_fin)
        duracion = timedelta(minutes=profesional.duracion_cita_min)

        while inicio + duracion <= fin_dia:
            fin_slot = inicio + duracion
            slots.append((inicio, fin_slot))
            inicio = fin_slot

        # Quitar slots ocupados
        citas_del_dia = self.db.query(Cita).filter(
            Cita.profesional_id == profesional.id,
            Cita.estado.in_(ESTADOS_ACTIVOS),
            Cita.inicio >= datetime.combine(fecha.date(), horario.hora_inicio),
            Cita.fin <= fin_dia,
        ).all()

        ocupados = {(c.inicio, c.fin) for c in citas_del_dia}

        return [
            SlotDisponibleSalida(inicio=s[0], fin=s[1])
            for s in slots if (s[0], s[1]) not in ocupados
        ]