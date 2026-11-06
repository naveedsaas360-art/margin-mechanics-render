# Generates 1920x1080 text cards from a JSON list: [{file,kicker,headline,sub,color}]
param([Parameter(Mandatory)][string]$Spec, [Parameter(Mandatory)][string]$OutDir)
Add-Type -AssemblyName System.Drawing
New-Item -ItemType Directory -Force $OutDir | Out-Null
$colors = @{ ink=[Drawing.Color]::FromArgb(14,17,22); yellow=[Drawing.Color]::FromArgb(255,197,49); green=[Drawing.Color]::FromArgb(43,214,123)
             red=[Drawing.Color]::FromArgb(255,77,77); white=[Drawing.Color]::White; grey=[Drawing.Color]::FromArgb(150,158,170) }
$px = [Drawing.GraphicsUnit]::Pixel
$fmt = New-Object Drawing.StringFormat; $fmt.Alignment='Center'
$W = 1640

foreach($c in (Get-Content $Spec -Raw -Encoding UTF8 | ConvertFrom-Json)){
  $bmp = New-Object Drawing.Bitmap 1920,1080; $g=[Drawing.Graphics]::FromImage($bmp)
  $g.SmoothingMode='AntiAlias'; $g.TextRenderingHint='AntiAliasGridFit'; $g.Clear($colors.ink)
  $hc = if($c.color){$colors[$c.color]}else{$colors.yellow}
  # shrink headline until it fits
  $size=150; do { $hf = New-Object Drawing.Font "Arial Black",$size,([Drawing.FontStyle]::Bold),$px
    $hs = $g.MeasureString($c.headline,$hf,$W,$fmt); $size-=8 } while($hs.Height -gt 480 -and $size -gt 50)
  $kf = New-Object Drawing.Font "Segoe UI",44,([Drawing.FontStyle]::Bold),$px
  $sf = New-Object Drawing.Font "Segoe UI",50,([Drawing.FontStyle]::Regular),$px
  $kh = if($c.kicker){70}else{0}; $sh = if($c.sub){ $g.MeasureString($c.sub,$sf,$W,$fmt).Height + 40 }else{0}
  $y = (1080 - ($kh + $hs.Height + $sh))/2
  if($c.kicker){ $g.DrawString($c.kicker,$kf,(New-Object Drawing.SolidBrush $colors.grey),(New-Object Drawing.RectangleF 140,$y,$W,80),$fmt); $y+=$kh }
  $g.DrawString($c.headline,$hf,(New-Object Drawing.SolidBrush $hc),(New-Object Drawing.RectangleF 140,$y,$W,($hs.Height+10)),$fmt); $y+=$hs.Height+40
  if($c.sub){ $g.DrawString($c.sub,$sf,(New-Object Drawing.SolidBrush $colors.white),(New-Object Drawing.RectangleF 140,$y,$W,$sh),$fmt) }
  $g.FillRectangle((New-Object Drawing.SolidBrush $hc),860,1000,200,8)
  $g.DrawString("MARGIN MECHANICS",(New-Object Drawing.Font "Segoe UI",26,([Drawing.FontStyle]::Bold),$px),(New-Object Drawing.SolidBrush $colors.grey),80,1010)
  $bmp.Save((Join-Path $OutDir $c.file),[Drawing.Imaging.ImageFormat]::Png); $g.Dispose(); $bmp.Dispose()
}
"Cards done: $OutDir"
