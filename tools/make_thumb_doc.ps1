# Documentary-style thumbnail: real photo, dark grade, bold hook text.
param([Parameter(Mandatory)][string]$Photo, [Parameter(Mandatory)][string]$Out, [string]$Sub = "explained in 11 minutes")
Add-Type -AssemblyName System.Drawing
$W=1280; $H=720
$bmp = New-Object Drawing.Bitmap $W,$H; $g=[Drawing.Graphics]::FromImage($bmp)
$g.SmoothingMode='AntiAlias'; $g.TextRenderingHint='AntiAliasGridFit'; $g.InterpolationMode='HighQualityBicubic'
$src = [Drawing.Image]::FromFile((Resolve-Path $Photo).Path)
$s = [Math]::Max($W/$src.Width, $H/$src.Height) * 1.12; $dw=$src.Width*$s; $dh=$src.Height*$s
$g.DrawImage($src, [single]($W-$dw), [single](($H-$dh)/2), [single]$dw, [single]$dh); $src.Dispose()
$grad = New-Object Drawing.Drawing2D.LinearGradientBrush ([Drawing.Point]::new(0,0)), ([Drawing.Point]::new($W,0)), ([Drawing.Color]::FromArgb(245,8,10,14)), ([Drawing.Color]::FromArgb(40,8,10,14))
$g.FillRectangle($grad,0,0,$W,$H)
$px=[Drawing.GraphicsUnit]::Pixel
function F($n,$face="Arial Black"){ New-Object Drawing.Font $face,$n,([Drawing.FontStyle]::Bold),$px }
$yel=[Drawing.Color]::FromArgb(255,197,49); $red=[Drawing.Color]::FromArgb(255,77,77)
$g.FillRectangle((New-Object Drawing.SolidBrush $yel),58,72,14,300)
$g.DrawString("THE AI",(F 92),[Drawing.Brushes]::White,80,60)
$g.DrawString("MONEY",(F 112),(New-Object Drawing.SolidBrush $yel),74,160)
$g.DrawString("LOOP",(F 112),[Drawing.Brushes]::White,74,275)
$tf = F 72; $tw = $g.MeasureString("-`$1 TRILLION",$tf).Width
$g.FillRectangle((New-Object Drawing.SolidBrush $red),80,450,[single]($tw+24),118)
$g.DrawString("-`$1 TRILLION",$tf,[Drawing.Brushes]::White,92,468)
$g.DrawString($Sub,(F 40 "Segoe UI"),(New-Object Drawing.SolidBrush ([Drawing.Color]::FromArgb(230,255,255,255))),84,600)
$bmp.Save($Out,[Drawing.Imaging.ImageFormat]::Png); $g.Dispose(); $bmp.Dispose(); "saved $Out"
