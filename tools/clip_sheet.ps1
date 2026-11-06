# Contact sheet of every resolved clip thumbnail, numbered, for visual QA.
param([Parameter(Mandatory)][string]$Episode)
Add-Type -AssemblyName System.Drawing
$root = Split-Path $PSScriptRoot -Parent
$cfg = Get-Content "$root\$Episode\scenes.json" -Raw -Encoding UTF8 | ConvertFrom-Json
$clips = @(); $seen = @{}
foreach($o in $cfg.outputs){ foreach($s in $o.scenes){ foreach($e in $s.elements){
  if(($e.type -eq 'clip' -or $e.type -eq 'shot') -and $e.url -and -not $seen.ContainsKey($e.url)){ $seen[$e.url] = 1; $clips += $e } } } }
$cols = 4; $tw = 400; $th = 225; $rows = [math]::Ceiling($clips.Count / $cols)
$bmp = New-Object Drawing.Bitmap ($cols*$tw), ($rows*($th+40)); $g = [Drawing.Graphics]::FromImage($bmp); $g.Clear([Drawing.Color]::White)
$font = New-Object Drawing.Font "Segoe UI",14,([Drawing.FontStyle]::Bold)
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$wc = New-Object Net.WebClient; $wc.Headers.Add("User-Agent","MarginMechanics/1.0 (educational YouTube channel)")
for($i=0; $i -lt $clips.Count; $i++){
  $x = ($i % $cols) * $tw; $y = [math]::Floor($i / $cols) * ($th+40)
  try { $img = [Drawing.Image]::FromStream((New-Object IO.MemoryStream (,$wc.DownloadData($(if($clips[$i].kind -eq 'image'){ $clips[$i].url } else { $clips[$i].thumb }))))); $g.DrawImage($img, $x, $y, $tw-6, $th); $img.Dispose() } catch {}
  $g.DrawString("$i  $($clips[$i].q)$($clips[$i].img)", $font, [Drawing.Brushes]::Black, $x+4, $y+$th+6)
}
$out = "$root\$Episode\clip_sheet.jpg"; $bmp.Save($out, [Drawing.Imaging.ImageFormat]::Jpeg); "saved $out ($($clips.Count) clips)"
