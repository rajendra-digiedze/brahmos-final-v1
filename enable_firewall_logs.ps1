Write-Host "Enabling OS-Level network packet logging for Windows Defender Firewall..."

# Enable Dropped Connections globally
netsh advfirewall set allprofiles logging droppedconnections enable

# Enable Allowed Connections globally
netsh advfirewall set allprofiles logging allowedconnections enable

Write-Host ""
Write-Host "Real-time Firewall Capture active! Logs are now piping into C:\Windows\System32\LogFiles\Firewall\pfirewall.log"
Write-Host "Press enter to exit."
Read-Host
