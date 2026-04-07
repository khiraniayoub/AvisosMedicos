# Guía Definitiva: Crear Webhook para Avisos (Nuevo Método)

Microsoft ha cambiado el sistema y el antiguo ya no funciona bien. Para que los avisos lleguen **sí o sí**, sigue estos pasos exactos para crear un "Workflow" compatible.

## 1. Crear el Workflow
1. En Teams, ve a **Aplicaciones** (Apps) en la barra izquierda.
2. Busca y abre la app **"Workflows"** (Flujos de trabajo).
3. Pestaña **Crear** (Create).
4. En el buscador escribe: `webhook`.
5. Selecciona la plantilla que se llama:
   👉 **"Publicar en un canal cuando se reciba una solicitud de webhook"** 
   *(Post to a channel when a webhook request is received)*.

## 2. Configurar (¡Importante!)
1. Dale un nombre (ej: "Avisos App").
2. Dale a **Siguiente**.
3. Te pedirá elegir **Equipo** y **Canal**. Elígelos.
4. **Dale a Crear**.

## 3. Copiar la URL
1. Una vez creado, te mostrará una **URL Larga**.
2. Cópiala.

## 4. Probar en la App
1. Ve a tu App de Avisos.
2. Pulsa la rueda dentada **⚙️**.
3. Pega esta **NUEVA URL**.
4. Intenta enviar.

---
**¿Por qué hacemos esto?**
El enlace que tenías antes probablemente era de un tipo "privado" o con un formato antiguo que rechaza nuestros mensajes. Esta plantilla nueva es la estándar y aceptará las tarjetas que envía la app.
