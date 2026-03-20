# Future publishing

Future publishing should plug into the social workspace through an adapter layer, not by replacing draft storage or approval logic.

Likely future adapters:
- Upload-Post API
- direct LinkedIn publishing
- Canva or other design/export integrations
- video generation/upload tools

Rule:
Keep vendor-specific parameters in the adapter layer. Preserve a vendor-neutral internal draft schema.
