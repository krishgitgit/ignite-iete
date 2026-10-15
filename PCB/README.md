# AuraPump --- Project Markdown Pack

This folder contains project instructions for using GPT Desktop or
another desktop agent to create AuraPump documentation and flowcharts.

## Files

-   `project-brief.md` --- project purpose, hardware inventory,
    constraints, and architecture.
-   `hardware-flowchart-prompt.md` --- prompt for the hardware/IoT
    flowchart, ending at the software-layer handoff.
-   `software-flowchart-prompt.md` --- prompt for the farmer-facing
    software layer and Gnani AI calling workflow.
-   `hardware-flow-explained.md` --- plain-language explanation of each
    component and the complete hardware flow.

## Important constraints

-   TinyML and reinforcement learning have been removed.
-   The ESP32 must make local protection decisions; software/AI/cloud
    must not be required for shutdown.
-   The 3--5 major-component limit must be confirmed with organisers;
    the full inventory below is a proposed architecture, not an approved
    allocation.
-   Do not invent sensor thresholds, accuracy, response times, or Gnani
    API capabilities.
-   A relay's contact state is not the same as the ESP32's HIGH/LOW
    control signal. Verify the exact module.
-   A local ESP32 Wi-Fi access point alone cannot make outbound phone
    calls. A backend and internet-connected calling service are
    required.
