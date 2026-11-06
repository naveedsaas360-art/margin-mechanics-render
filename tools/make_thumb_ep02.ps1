# EP02 thumbnail (1280x720): hand-drawn money loop + headline.
param([string]$Out = "$PSScriptRoot\..\EP02_AI_Money_Loop\thumbnail.png")
Add-Type -AssemblyName System.Drawing
$PAPER = [Drawing.Color]::FromArgb(251,250,246); $INK = [Drawing.Color]::FromArgb(30,30,36)
$BLUE = [Drawing.Color]::FromArgb(31,95,191); $RED = [Drawing.Color]::FromArgb(215,54,43)
$GREEN = [Drawing.Color]::FromArgb(27,158,90); $ORANGE = [Drawing.Color]::FromArgb(232,135,30)
$YEL = [Drawing.Color]::FromArgb(170,255,216,77)
$px = [Drawing.GraphicsUnit]::Pixel
$bmp = New-Object Drawing.Bitmap 1280,720; $g = [Drawing.Graphics]::FromImage($bmp)
$g.SmoothingMode='AntiAlias'; $g.TextRenderingHint='AntiAliasGridFit'; $g.Clear($PAPER)
function F($size,$face="Arial Black"){ New-Object Drawing.Font $face,$size,([Drawing.FontStyle]::Bold),$px }
function Txt($s,$f,$c,$x,$y){ $g.DrawString($s,$f,(New-Object Drawing.SolidBrush $c),[single]$x,[single]$y) }
function CTxt($s,$f,$c,$cx,$cy){ $sz=$g.MeasureString($s,$f); Txt $s $f $c ($cx-$sz.Width/2) ($cy-$sz.Height/2) }
function Arc($c,$x,$y,$w,$h,$a,$sweep){
  $p = New-Object Drawing.Pen $c,16; $p.StartCap='Round'; $p.CustomEndCap = New-Object Drawing.Drawing2D.AdjustableArrowCap 3.2,3.2
  $g.DrawArc($p,$x,$y,$w,$h,$a,$sweep)
  $p2 = New-Object Drawing.Pen ([Drawing.Color]::FromArgb(90,$c)),6; $g.DrawArc($p2,$x+8,$y-6,$w-12,$h+10,$a+4,$sweep-10)
}
# loop: three arcs between three nodes on a circle
$cx=330; $cy=380; $r=230
Arc $GREEN ($cx-$r) ($cy-$r) (2*$r) (2*$r) -75 95
Arc $ORANGE ($cx-$r) ($cy-$r) (2*$r) (2*$r) 50 95
Arc $RED ($cx-$r) ($cy-$r) (2*$r) (2*$r) 172 88
function Node($label,$color,$x,$y){
  $g.FillEllipse((New-Object Drawing.SolidBrush $PAPER),$x-95,$y-48,190,96)
  $g.DrawEllipse((New-Object Drawing.Pen $color,7),$x-95,$y-48,190,96)
  CTxt $label (F 30) $color $x $y
}
Node "NVIDIA" $BLUE ($cx) ($cy-$r)
Node "OpenAI" $GREEN ($cx+$r*0.87) ($cy+$r*0.5)
Node "CLOUD" $ORANGE ($cx-$r*0.87) ($cy+$r*0.5)
CTxt "$" (F 120) $GREEN $cx ($cy+10)
# headline
function Fit($s,$max,$w){ $n=$max; do { $f = F $n; $n -= 2 } while($g.MeasureString($s,$f).Width -gt $w); $f }
$f2 = Fit "MONEY LOOP" 100 600; $w2 = $g.MeasureString("MONEY LOOP",$f2).Width
$g.FillRectangle((New-Object Drawing.SolidBrush $YEL),650,118,[single]($w2-20),[single]($f2.Size*0.95))
Txt "THE AI" $f2 $INK 640 20
Txt "MONEY LOOP" $f2 $INK 640 115
Txt "-`$1 TRILLION" (Fit "-`$1 TRILLION" 100 600) $RED 640 300
$u = New-Object Drawing.Pen $RED,10; $u.StartCap='Round'; $u.EndCap='Round'
$g.DrawBezier($u,650,435,850,450,1000,425,1230,440)
Txt "explained simply" (F 52 "Segoe Print") $BLUE 700 500
$bmp.Save($Out,[Drawing.Imaging.ImageFormat]::Png); $g.Dispose(); $bmp.Dispose()
"saved $Out"
