import os
from twilio.rest import Client
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.modelos.notificacion_modelo import Notificacion
from app.modelos.cita_modelo import Cita

# ── Credenciales desde .env ───────────────────────────────────────────
ACCOUNT_SID  = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN   = os.getenv("TWILIO_AUTH_TOKEN")
FROM_NUMBER  = os.getenv("TWILIO_WHATSAPP_FROM")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")


class NotificacionServicio:

    def __init__(self, db: Session):
        self.db = db
        self.client = Client(ACCOUNT_SID, AUTH_TOKEN)

    # ==================================================================
    # 🔒 MÉTODOS PRIVADOS — uso interno
    # ==================================================================

    def _enviar_whatsapp(self, telefono: str, mensaje: str) -> bool:
        """
        Envía un mensaje de WhatsApp real vía Twilio.
        El teléfono debe tener formato internacional: +593991234567
        Retorna True si fue exitoso, False si falló.
        """
        try:
            destinatario = f"whatsapp:{telefono}"
            self.client.messages.create(
                body=mensaje,
                from_=FROM_NUMBER,
                to=destinatario,
            )
            print(f"✅ WhatsApp enviado a {telefono}")
            return True
        except Exception as e:
            print(f"⚠️ Error al enviar WhatsApp a {telefono}: {str(e)}")
            return False

    def _registrar_notificacion(
        self,
        cita_id: int,
        telefono: str,
        tipo: str,
        programada_para: datetime,
    ) -> Notificacion:
        """
        Guarda el registro de la notificación en la DB antes de enviar.
        Así tenemos trazabilidad de todo lo que se intentó enviar.
        """
        notif = Notificacion(
            cita_id=cita_id,
            telefono_dest=telefono,
            tipo=tipo,
            canal="whatsapp",
            estado="pendiente",
            programada_para=programada_para,
        )
        self.db.add(notif)
        self.db.flush()
        return notif

    def _marcar_resultado(
        self,
        notif: Notificacion,
        exito: bool,
    ) -> None:
        """
        Actualiza el estado de la notificación según si se envió o no.
        """
        notif.estado   = "enviada" if exito else "fallida"
        notif.enviada_en = datetime.utcnow() if exito else None
        self.db.commit()

    # ==================================================================
    # 📨 NOTIFICACIONES AL PACIENTE
    # ==================================================================

    def enviar_confirmacion(
        self,
        cita: Cita,
        nombre_paciente: str,
        nombre_profesional: str,
        telefono: str,
    ) -> None:
        """
        RF-07 — Se llama inmediatamente cuando el paciente reserva.
        El paciente recibe confirmación + link para cancelar.
        """
        link_cancelar = f"{FRONTEND_URL}/cancelar/{cita.token_reserva}"

        mensaje = (
            f"✅ *Cita confirmada*\n\n"
            f"Hola {nombre_paciente}, tu cita ha sido confirmada.\n\n"
            f"👨‍⚕️ *Profesional:* Dr(a). {nombre_profesional}\n"
            f"📅 *Fecha:* {cita.inicio.strftime('%d/%m/%Y')}\n"
            f"🕐 *Hora:* {cita.inicio.strftime('%H:%M')}\n"
            f"📝 *Motivo:* {cita.motivo}\n\n"
            f"¿No puedes asistir? Cancela aquí:\n"
            f"{link_cancelar}\n\n"
            f"¡Te esperamos!"
        )

        notif = self._registrar_notificacion(
            cita_id=cita.id,
            telefono=telefono,
            tipo="confirmacion",
            programada_para=datetime.utcnow(),
        )
        exito = self._enviar_whatsapp(telefono, mensaje)
        self._marcar_resultado(notif, exito)

    def enviar_recordatorio_2dias(
        self,
        cita: Cita,
        nombre_paciente: str,
        nombre_profesional: str,
        telefono: str,
    ) -> None:
        """
        RF-07 — Recordatorio 2 días antes de la cita.
        Lo llama el scheduler automáticamente.
        """
        link_cancelar = f"{FRONTEND_URL}/cancelar/{cita.token_reserva}"

        mensaje = (
            f"📅 *Recordatorio de cita*\n\n"
            f"Hola {nombre_paciente}, en *2 días* tienes cita.\n\n"
            f"👨‍⚕️ *Profesional:* Dr(a). {nombre_profesional}\n"
            f"📅 *Fecha:* {cita.inicio.strftime('%d/%m/%Y')}\n"
            f"🕐 *Hora:* {cita.inicio.strftime('%H:%M')}\n\n"
            f"¿No puedes asistir? Cancela aquí:\n"
            f"{link_cancelar}"
        )

        programada = cita.inicio - timedelta(days=2)
        notif = self._registrar_notificacion(
            cita_id=cita.id,
            telefono=telefono,
            tipo="recordatorio_2dias",
            programada_para=programada,
        )
        exito = self._enviar_whatsapp(telefono, mensaje)
        self._marcar_resultado(notif, exito)

    def enviar_recordatorio_24h(
        self,
        cita: Cita,
        nombre_paciente: str,
        nombre_profesional: str,
        telefono: str,
    ) -> None:
        """
        RF-07 — Recordatorio 24 horas antes de la cita.
        Lo llama el scheduler automáticamente.
        """
        link_cancelar = f"{FRONTEND_URL}/cancelar/{cita.token_reserva}"

        mensaje = (
            f"🔔 *Recordatorio — mañana tienes cita*\n\n"
            f"Hola {nombre_paciente}, mañana tienes cita.\n\n"
            f"👨‍⚕️ *Profesional:* Dr(a). {nombre_profesional}\n"
            f"📅 *Fecha:* {cita.inicio.strftime('%d/%m/%Y')}\n"
            f"🕐 *Hora:* {cita.inicio.strftime('%H:%M')}\n\n"
            f"¿No puedes asistir? Cancela aquí:\n"
            f"{link_cancelar}"
        )

        programada = cita.inicio - timedelta(hours=24)
        notif = self._registrar_notificacion(
            cita_id=cita.id,
            telefono=telefono,
            tipo="recordatorio_24h",
            programada_para=programada,
        )
        exito = self._enviar_whatsapp(telefono, mensaje)
        self._marcar_resultado(notif, exito)

    def enviar_recordatorio_2h(
        self,
        cita: Cita,
        nombre_paciente: str,
        nombre_profesional: str,
        telefono: str,
    ) -> None:
        """
        RF-07 — Recordatorio 2 horas antes de la cita.
        Lo llama el scheduler automáticamente.
        """
        link_cancelar = f"{FRONTEND_URL}/cancelar/{cita.token_reserva}"

        mensaje = (
            f"⏰ *Tu cita es en 2 horas*\n\n"
            f"Hola {nombre_paciente}, recuerda que en "
            f"*2 horas* tienes cita.\n\n"
            f"👨‍⚕️ *Profesional:* Dr(a). {nombre_profesional}\n"
            f"🕐 *Hora:* {cita.inicio.strftime('%H:%M')}\n\n"
            f"¿No puedes asistir? Cancela aquí:\n"
            f"{link_cancelar}"
        )

        programada = cita.inicio - timedelta(hours=2)
        notif = self._registrar_notificacion(
            cita_id=cita.id,
            telefono=telefono,
            tipo="recordatorio_2h",
            programada_para=programada,
        )
        exito = self._enviar_whatsapp(telefono, mensaje)
        self._marcar_resultado(notif, exito)

    def enviar_cancelacion_paciente(
        self,
        cita: Cita,
        nombre_paciente: str,
        nombre_profesional: str,
        telefono: str,
    ) -> None:
        """
        RF-07 — Avisa al paciente que su cita fue cancelada.
        Se llama desde cita_servicio.cancelar()
        """
        mensaje = (
            f"❌ *Cita cancelada*\n\n"
            f"Hola {nombre_paciente}, tu cita ha sido cancelada.\n\n"
            f"👨‍⚕️ *Profesional:* Dr(a). {nombre_profesional}\n"
            f"📅 *Fecha:* {cita.inicio.strftime('%d/%m/%Y')}\n"
            f"🕐 *Hora:* {cita.inicio.strftime('%H:%M')}\n\n"
            f"Si deseas reagendar escríbenos o entra al link "
            f"del profesional para reservar nuevamente."
        )

        notif = self._registrar_notificacion(
            cita_id=cita.id,
            telefono=telefono,
            tipo="cancelacion_paciente",
            programada_para=datetime.utcnow(),
        )
        exito = self._enviar_whatsapp(telefono, mensaje)
        self._marcar_resultado(notif, exito)

    # ==================================================================
    # 📨 NOTIFICACIONES AL PROFESIONAL
    # ==================================================================

    def notificar_profesional_nueva_cita(
        self,
        cita: Cita,
        nombre_paciente: str,
        nombre_profesional: str,
        telefono_profesional: str,
    ) -> None:
        """
        RF-07 — Avisa al profesional cuando llega una reserva nueva.
        Se llama desde cita_servicio.reservar()
        """
        link_panel = f"{FRONTEND_URL}/panel/citas"

        mensaje = (
            f"📋 *Nueva cita agendada*\n\n"
            f"Hola Dr(a). {nombre_profesional},\n"
            f"tienes una nueva cita.\n\n"
            f"👤 *Paciente:* {nombre_paciente}\n"
            f"📅 *Fecha:* {cita.inicio.strftime('%d/%m/%Y')}\n"
            f"🕐 *Hora:* {cita.inicio.strftime('%H:%M')}\n"
            f"📝 *Motivo:* {cita.motivo}\n\n"
            f"Ver todas tus citas:\n{link_panel}"
        )

        notif = self._registrar_notificacion(
            cita_id=cita.id,
            telefono=telefono_profesional,
            tipo="nueva_reserva_pro",
            programada_para=datetime.utcnow(),
        )
        exito = self._enviar_whatsapp(telefono_profesional, mensaje)
        self._marcar_resultado(notif, exito)

    def notificar_profesional_cancelacion(
        self,
        cita: Cita,
        nombre_paciente: str,
        nombre_profesional: str,
        telefono_profesional: str,
    ) -> None:
        """
        RF-07 — Avisa al profesional que una cita fue cancelada.
        Se llama desde cita_servicio.cancelar()
        """
        link_panel = f"{FRONTEND_URL}/panel/citas"

        mensaje = (
            f"❌ *Cita cancelada*\n\n"
            f"Dr(a). {nombre_profesional}, una cita fue cancelada.\n\n"
            f"👤 *Paciente:* {nombre_paciente}\n"
            f"📅 *Fecha:* {cita.inicio.strftime('%d/%m/%Y')}\n"
            f"🕐 *Hora:* {cita.inicio.strftime('%H:%M')}\n\n"
            f"El horario quedó disponible nuevamente.\n"
            f"Ver tu agenda: {link_panel}"
        )

        notif = self._registrar_notificacion(
            cita_id=cita.id,
            telefono=telefono_profesional,
            tipo="cancelacion_profesional",
            programada_para=datetime.utcnow(),
        )
        exito = self._enviar_whatsapp(telefono_profesional, mensaje)
        self._marcar_resultado(notif, exito)

    def enviar_resumen_diario(
        self,
        nombre_profesional: str,
        telefono_profesional: str,
        citas: list,
    ) -> None:
        """
        RF-07 — Resumen de citas del día al profesional cada mañana.
        Lo llama el scheduler a las 7am.
        """
        if not citas:
            mensaje = (
                f"📅 *Agenda del día*\n\n"
                f"Buenos días Dr(a). {nombre_profesional},\n"
                f"hoy no tienes citas agendadas.\n\n"
                f"¡Buen día! 🌟"
            )
        else:
            lista_citas = ""
            for cita in citas:
                lista_citas += (
                    f"🕐 {cita.inicio.strftime('%H:%M')} — "
                    f"{cita.paciente.nombre_completo}\n"
                )

            mensaje = (
                f"📅 *Agenda del día*\n\n"
                f"Buenos días Dr(a). {nombre_profesional},\n"
                f"tienes *{len(citas)} cita(s)* hoy:\n\n"
                f"{lista_citas}\n"
                f"¡Buen día! 🌟"
            )

        exito = self._enviar_whatsapp(telefono_profesional, mensaje)
        if exito:
            print(f"✅ Resumen diario enviado a Dr(a). {nombre_profesional}")
        else:
            print(f"⚠️ No se pudo enviar resumen a Dr(a). {nombre_profesional}")