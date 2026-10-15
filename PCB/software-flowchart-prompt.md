# Prompt: AuraPump Software Layer, Farmer-Friendly App and Gnani AI

Act as a senior product architect, rural UX designer, IoT software
engineer, and voice-AI integration specialist. Create a professional
flowchart for the software layer of AuraPump, an IGNITE 1.0 IETE IoT
Hackathon project.

## Product goal

AuraPump is intended for farmers who may not understand technical
graphs, may not prefer English or Hindi, and may miss app notifications.
The software must explain important events in simple language and, when
configured, proactively call the farmer in a preferred supported
language through Gnani AI.

The goal is not a conventional engineering dashboard. The farmer should
be able to understand: - Is the pump working? - What happened? - Has the
system stopped the pump? - What should I check? - Was I successfully
contacted?

## Input from hardware

The ESP32 sends telemetry and events that may include: - device ID and
timestamp; - current, voltage, temperature and water flow; - TDS,
turbidity and soil-moisture readings if available; - pump state; - fault
category and severity; - sensor-health flags; - relay command and any
verified shutdown status.

The ESP32 remains responsible for local protection. The app, backend,
internet and AI must not be required for shutdown.

## Required flowchart sequence

### 1. Telemetry ingestion

-   Receive telemetry and fault events from AuraPump hardware layer.
-   Validate device identity, event structure, timestamps and
    measurement validity.
-   Decision: Is the data valid and current?
    -   No: mark status as unavailable or stale; do not display an
        assumed healthy state; follow reconnection policy.
    -   Yes: update latest device state and event record.

### 2. Interpret event

Classify the incoming record using validated rules into: - normal
operation; - possible dry running or abnormal water flow; - overload; -
voltage anomaly; - overheating; - sensor failure; - water-quality
warning; - low soil moisture / irrigation observation.

Distinguish pump-protection events from agricultural advisory events.
Use actual evidence. Do not let an LLM invent faults or override
protection.

### 3. Alert priority

-   Determine event severity and communication preferences.
-   Critical fault or protective shutdown: start configured voice-call
    workflow.
-   Lower-priority event: update app and event history according to
    preferences.
-   Deduplicate repeated events and avoid excessive calls for one
    unresolved fault.

### 4. Gnani AI calling workflow

-   Retrieve farmer's verified phone number, preferred supported
    language and consent.
-   Prepare a concise, approved explanation based on actual event data.
-   Invoke the configured Gnani AI outbound calling integration if
    available.
-   Deliver message in the selected supported language.

Example: "Your pump has been stopped because water flow appears
abnormal. Please check the water source and pipes before restarting."

Explain: - what happened; - what the system did; - what the farmer
should check; - whether the diagnosis is confirmed or suspected.

Decision: Was the call answered and acknowledged? - Yes: record
acknowledgement and supported response. - No: apply bounded retries and,
if configured, notify an authorised alternate contact or technician.

Do not treat an unanswered call as acknowledged. Do not automatically
restart the pump from a voice response. Any restart must follow hardware
safe-recovery rules.

### 5. Farmer-friendly mobile app

Show: - large status: **Working**, **Needs Attention**, **Stopped for
Protection**, or **Status Unavailable**; - simple icons and
plain-language messages; - explanation of latest fault; - recommended
checks and safe next steps; - voice playback of explanation; -
preferred-language settings; - call status and acknowledgement
history; - recent events and maintenance history.

Keep raw electrical values and detailed charts in an optional
technician/advanced view. A farmer must not need to interpret graphs to
understand pump status.

### 6. Conversational assistance

If enabled, let the farmer ask: - Why did my pump stop? - What should I
check? - Can you repeat the message? - Can I contact a technician?

Retrieve the relevant event and approved troubleshooting instructions
before generating a response. Do not invent readings, claim unsupported
diagnoses, provide unsafe electrical repair instructions, or override a
protective shutdown.

### 7. Failure handling

-   If the phone has no internet, physical pump protection continues
    locally.
-   If backend cannot reach the device, show status as
    stale/unavailable.
-   If Gnani AI or calling service is unavailable, retain the event and
    mark call pending/failed.
-   If connectivity returns, transmit buffered events only if supported
    and avoid duplicate or misleading alerts.

### 8. End states

Show two outcomes: - **Farmer informed:** relevant information was
received and acknowledged where acknowledgement is supported. -
**Follow-up required:** event remains unresolved or call was not
acknowledged, so configured follow-up is initiated.

## Explain the design choice

Include a small rationale: - Conventional dashboards show graphs, raw
sensor values and technical alerts, expecting the farmer to open the app
and interpret them. - AuraPump turns actual events into plain-language
status, proactive calls in the farmer's selected supported language,
practical next steps, and a complementary mobile interface.

## Gnani AI constraints

-   Show Gnani AI as an external voice/telephony service.
-   Do not invent API endpoints, SDKs, supported languages, pricing, or
    call-delivery capabilities.
-   Mark outbound calling as dependent on account/API access,
    connectivity, language support and required consent.
-   Separate fault classification from natural-language explanation.
-   Keep the system useful if the voice service is unavailable.

## Diagram requirements

-   Valid Mermaid syntax, top-to-bottom layout.
-   Separate sections for telemetry ingestion, event interpretation,
    alert decision, Gnani calling, farmer app, conversational
    assistance, acknowledgement/follow-up and failure handling.
-   Use standard shapes and explicit decision branches.
-   Restrained navy/white/teal palette, amber warnings and red critical
    faults if rendered.
-   Avoid crossing lines and excessive detail.
-   Start with **"Receive telemetry and fault events from AuraPump
    hardware layer"**.
-   Do not duplicate hardware sensor acquisition or relay control.

## Deliverables

1.  Complete valid Mermaid source.
2.  Rendered diagram if supported.
3.  Short explanation of the farmer-first design.
4.  Dependencies requiring verification, especially Gnani integration
    and supported languages.

Prioritise accessibility, honest fault reporting, safe recovery and
realistic hackathon implementation.
