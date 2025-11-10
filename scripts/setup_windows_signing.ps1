# PowerShell script to set up code signing for Windows builds
# This creates a self-signed certificate for testing purposes
# For production, you should use a certificate from a trusted CA

param(
    [string]$CertName = "FM Skin Builder",
    [string]$OutputPath = ".",
    [string]$Password = ""
)

Write-Host "Setting up Windows code signing certificate..." -ForegroundColor Green

# Generate a password if not provided
if ([string]::IsNullOrEmpty($Password)) {
    $Password = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 16 | ForEach-Object {[char]$_})
    Write-Host "Generated password: $Password" -ForegroundColor Yellow
    Write-Host "IMPORTANT: Save this password securely!" -ForegroundColor Red
}

$SecurePassword = ConvertTo-SecureString -String $Password -Force -AsPlainText

# Create a self-signed certificate
Write-Host "Creating self-signed certificate..." -ForegroundColor Cyan
$Cert = New-SelfSignedCertificate `
    -Type CodeSigning `
    -Subject "CN=$CertName" `
    -KeyUsage DigitalSignature `
    -FriendlyName "$CertName Code Signing" `
    -CertStoreLocation "Cert:\CurrentUser\My" `
    -TextExtension @("2.5.29.37={text}1.3.6.1.5.5.7.3.3", "2.5.29.19={text}") `
    -NotAfter (Get-Date).AddYears(3)

Write-Host "Certificate created with thumbprint: $($Cert.Thumbprint)" -ForegroundColor Green

# Export the certificate to a PFX file
$PfxPath = Join-Path $OutputPath "signing-cert.pfx"
Export-PfxCertificate -Cert $Cert -FilePath $PfxPath -Password $SecurePassword

Write-Host "Certificate exported to: $PfxPath" -ForegroundColor Green

# Output instructions
Write-Host "`n=== Setup Complete ===" -ForegroundColor Green
Write-Host "`nTo use this certificate:" -ForegroundColor Yellow
Write-Host "1. Add the certificate thumbprint to tauri.conf.json:" -ForegroundColor White
Write-Host "   `"certificateThumbprint`": `"$($Cert.Thumbprint)`"" -ForegroundColor Gray
Write-Host "`n2. For GitHub Actions, add these secrets:" -ForegroundColor White
Write-Host "   WINDOWS_CERTIFICATE: (base64 of signing-cert.pfx)" -ForegroundColor Gray
Write-Host "   WINDOWS_CERTIFICATE_PASSWORD: $Password" -ForegroundColor Gray
Write-Host "`n3. To encode certificate for GitHub:" -ForegroundColor White
Write-Host "   [Convert]::ToBase64String([IO.File]::ReadAllBytes('$PfxPath'))" -ForegroundColor Gray
Write-Host "`nWARNING: Self-signed certificates will show security warnings." -ForegroundColor Red
Write-Host "For production, obtain a certificate from a trusted CA like DigiCert or Sectigo." -ForegroundColor Red
