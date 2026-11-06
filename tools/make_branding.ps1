# Channel art: profile picture (800x800), banner (2560x1440), watermark (150x150).
param([string]$Out = "$PSScriptRoot\..\branding")
Add-Type -AssemblyName System.Drawing
New-Item -ItemType Directory -Force $Out | Out-Null
$PAPER = [Drawing.Color]::FromArgb(251,250,246); $INK = [Drawing.Color]::FromArgb(30,30,36)
$BLUE = [Drawing.Color]::FromArgb(31,95,191); $YEL = [Drawing.Color]::FromArgb(150,255,216,77)
$RED = [Drawing.Color]::FromArgb(215,54,43); $GREEN = [Drawing.Color]::FromArgb(27,158,90); $GREY = [Drawing.Color]::FromArgb(110,110,120)
$px = [Drawing.GraphicsUnit]::Pixel
function Canvas($w,$h,$bg){ $b = New-Object Drawing.Bitmap $w,$h; $g=[Drawing.Graphics]::FromImage($b)
  $g.SmoothingMode='AntiAlias'; $g.TextRenderingHint='AntiAliasGridFit'; $g.Clear($bg); @($b,$g) }
function Pen($c,$w){ $p = New-Object Drawing.Pen $c,$w; $p.StartCap='Round'; $p.EndCap='Round'; $p.LineJoin='Round'; $p }
function Center($g,$s,$font,$color,$cx,$cy){ $sz=$g.MeasureString($s,$font); $g.DrawString($s,$font,(New-Object Drawing.SolidBrush $color),[single]($cx-$sz.Width/2),[single]($cy-$sz.Height/2)) }
# sketchy double-stroke ellipse
function Loop($g,$c,$w,$x,$y,$rw,$rh){ $g.DrawEllipse((Pen $c $w),$x,$y,$rw,$rh); $g.DrawEllipse((Pen $c ($w*0.6)),$x+6,$y-4,$rw-10,$rh+6) }
# little rising bar chart with arrow
function Chart($g,$x,$y,$s){
  $g.FillRectangle((New-Object Drawing.SolidBrush $YEL),$x,$y-40*$s,30*$s,40*$s); $g.DrawRectangle((Pen $INK (4*$s)),$x,$y-40*$s,30*$s,40*$s)
  $g.FillRectangle((New-Object Drawing.SolidBrush $YEL),$x+42*$s,$y-70*$s,30*$s,70*$s); $g.DrawRectangle((Pen $INK (4*$s)),$x+42*$s,$y-70*$s,30*$s,70*$s)
  $g.FillRectangle((New-Object Drawing.SolidBrush $YEL),$x+84*$s,$y-110*$s,30*$s,110*$s); $g.DrawRectangle((Pen $INK (4*$s)),$x+84*$s,$y-110*$s,30*$s,110*$s)
  $p = Pen $GREEN (6*$s); $p.CustomEndCap = New-Object Drawing.Drawing2D.AdjustableArrowCap 4,4
  $g.DrawLine($p,$x-10*$s,$y-30*$s,$x+130*$s,$y-150*$s)
}

# Profile picture
$c = Canvas 800 800 $PAPER; $g=$c[1]
$g.FillEllipse((New-Object Drawing.SolidBrush $YEL),120,330,560,190)
Center $g "MM" (New-Object Drawing.Font "Arial Black",250,([Drawing.FontStyle]::Bold),$px) $BLUE 400 410
Loop $g $INK 14 70 120 660 580
$c[0].Save("$Out\profile_800.png",[Drawing.Imaging.ImageFormat]::Png); $g.Dispose(); $c[0].Dispose()

# Watermark (subscribe button overlay)
$c = Canvas 150 150 $PAPER; $g=$c[1]
$g.FillEllipse((New-Object Drawing.SolidBrush $BLUE),5,5,140,140)
Center $g "MM" (New-Object Drawing.Font "Arial Black",54,([Drawing.FontStyle]::Bold),$px) ([Drawing.Color]::White) 75 76
$c[0].Save("$Out\watermark_150.png",[Drawing.Imaging.ImageFormat]::Png); $g.Dispose(); $c[0].Dispose()

# Banner: everything important inside the 1546x423 centre safe area (507..2053, 508..931)
$c = Canvas 2560 1440 $PAPER; $g=$c[1]
$grid = Pen ([Drawing.Color]::FromArgb(18,30,30,36)) 2
for($x=0;$x -lt 2560;$x+=64){ $g.DrawLine($grid,$x,0,$x,1440) }; for($y=0;$y -lt 1440;$y+=64){ $g.DrawLine($grid,0,$y,2560,$y) }
$tf = New-Object Drawing.Font "Arial Black",104,([Drawing.FontStyle]::Bold),$px; $tw = $g.MeasureString("MARGIN MECHANICS",$tf).Width
$g.FillRectangle((New-Object Drawing.SolidBrush $YEL),[single](1280-$tw/2+20),610,[single]($tw-40),95)
Center $g "MARGIN MECHANICS" $tf $INK 1280 650
Center $g "The money behind the headlines, drawn simply." (New-Object Drawing.Font "Segoe Print",50,([Drawing.FontStyle]::Bold),$px) $BLUE 1280 790
Center $g "NEW VIDEOS EVERY TUESDAY & FRIDAY" (New-Object Drawing.Font "Segoe UI",34,([Drawing.FontStyle]::Bold),$px) $RED 1280 880
Chart $g 250 860 1.4
$coin = Pen $INK 6; $g.DrawEllipse($coin,2160,580,170,170); $g.DrawEllipse((Pen $INK 3),2185,605,120,120)
Center $g "$" (New-Object Drawing.Font "Arial Black",64,([Drawing.FontStyle]::Bold),$px) $GREEN 2245 663
$c[0].Save("$Out\banner_2560x1440.png",[Drawing.Imaging.ImageFormat]::Png); $g.Dispose(); $c[0].Dispose()
"Branding saved to $Out"
