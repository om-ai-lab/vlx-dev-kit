# Frequently Asked Questions

The following answers cover issues most often encountered by developers and operations teams. For further assistance, export a diagnostic package and contact technical support.
<span style="color: #1677B3;">Q:</span> **How do I troubleshoot a model startup failure?**

<span style="color: #009B72;">A:</span> Check the error code and view detailed logs on the “Diagnostics” page:

| Error code | Meaning |
| --- | --- |
| `VLX-LIC-001` | Device is not activated |
| `VLX-LIC-002` | Device identity mismatch |
| `VLX-LIC-003` | No entitlement for the requested model |
| `VLX-MDL-001` | Model failed to load |


<span style="color: #1677B3;">Q:</span> **How do I roll back after an upgrade failure?**

<span style="color: #009B72;">A:</span> The system automatically rolls back to the previous healthy version. The database is not rolled back automatically; backward compatibility keeps the old version available. Restore from a verified backup if necessary, then run a complete health check.

<span style="color: #1677B3;">Q:</span> **How do I activate offline?**

<span style="color: #009B72;">A:</span> See Section 6.2. In brief: export a request file → upload it to the VLX Licensing Portal → download the device license (`license.vlx`) → import it into the device. The device does not need network access.

<span style="color: #1677B3;">Q:</span> **How do I free up storage space?**

<span style="color: #009B72;">A:</span> View storage details on the “Diagnostics” page and remove historical task records, old upgrade packages, and expired logs. Run `vlx-backup create` first. Consider expanding external storage if capacity remains insufficient.

<span style="color: #1677B3;">Q:</span> **How do I connect remotely?**

<span style="color: #009B72;">A:</span> Remote terminals are disabled by default or restricted to the management subnet. When enabled, use a dedicated operations account and key authentication; never share the administrator password, and disable access after maintenance.

<span style="color: #1677B3;">Q:</span> **How do I export a diagnostic package?**

<span style="color: #009B72;">A:</span> On the “Diagnostics” page, click “Export diagnostic package,” choose the scope and redaction options, and download it. You can also export from the command line. The package contains version numbers, health status, and redacted logs; passwords, keys, images, and personal data are removed by default.
