# Combine cloud preview JPGs into one labelled contact sheet.
param([Parameter(Mandatory)][string]$Dir, [string]$Out = "$Dir\..\qa_sheet.jpg")
Add-Type -AssemblyName System.Drawing
$files = Get-ChildItem $Dir -Filter *.jpg | Sort-Object { [double]($_.BaseName -replace '.*_','') }
$cols = 6; $tw = 400; $th = 225; $rows = [math]::Ceiling($files.Count / $cols)
$b = New-Object Drawing.Bitmap ($cols*$tw), ($rows*($th+24)); $g = [Drawing.Graphics]::FromImage($b); $g.Clear([Drawing.Color]::White)
$f = New-Object Drawing.Font "Segoe UI",12,([Drawing.FontStyle]::Bold)
for($i=0;$i -lt $files.Count;$i++){ $img=[Drawing.Image]::FromFile($files[$i].FullName); $x=($i%$cols)*$tw; $y=[math]::Floor($i/$cols)*($th+24)
  $g.DrawImage($img,$x,$y,$tw-4,$th); $img.Dispose(); $g.DrawString("$i  ($($files[$i].BaseName -replace '.*_',''))",$f,[Drawing.Brushes]::Black,$x+4,$y+$th+2) }
$b.Save((Resolve-Path (Split-Path $Out)).Path + "\" + (Split-Path $Out -Leaf),[Drawing.Imaging.ImageFormat]::Jpeg); "saved"
