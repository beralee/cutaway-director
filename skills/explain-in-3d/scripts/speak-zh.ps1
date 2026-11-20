param(
    [Parameter(Mandatory)][string]$Plan,
    [string]$VoiceId = 'MSTTS_V110_zhCN_HuihuiM',
    [ValidateRange(-10,10)][int]$Rate = 1
)
$ErrorActionPreference = 'Stop'
$planPath = (Resolve-Path -LiteralPath $Plan).Path
$planDir = Split-Path -Parent $planPath
$story = Get-Content -LiteralPath $planPath -Raw -Encoding utf8 | ConvertFrom-Json
$token = New-Object -ComObject SAPI.SpObjectToken
$token.SetId("HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech_OneCore\Voices\Tokens\$VoiceId")
$speaker = New-Object -ComObject SAPI.SpVoice
$speaker.Voice = $token
$speaker.Rate = $Rate
foreach ($shot in $story.shots) {
    $audioPath = [IO.Path]::GetFullPath([IO.Path]::Combine($planDir, $shot.audio))
    if ([IO.Path]::GetExtension($audioPath) -ne '.wav') { throw 'Choose a WAV path for synthesized audio.' }
    [IO.Directory]::CreateDirectory([IO.Path]::GetDirectoryName($audioPath)) | Out-Null
    $tempPath = "$audioPath.$([guid]::NewGuid().ToString('N')).wav"
    $stream = New-Object -ComObject SAPI.SpFileStream
    try {
        $stream.Open($tempPath, 3)
        $speaker.AudioOutputStream = $stream
        $speaker.Speak([string]$shot.line, 16) | Out-Null
    } finally {
        $stream.Close()
    }
    Move-Item -LiteralPath $tempPath -Destination $audioPath -Force
}
