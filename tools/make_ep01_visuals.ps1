# Generates EP01 charts (1920x1080) and thumbnail (1280x720) with built-in .NET System.Drawing.
param([string]$Out = "$PSScriptRoot\..\EP01_Costco")
Add-Type -AssemblyName System.Drawing
$vis = Join-Path $Out "visuals"; New-Item -ItemType Directory -Force $vis | Out-Null

$INK = [Drawing.Color]::FromArgb(14,17,22); $PANEL = [Drawing.Color]::FromArgb(28,33,42)
$YEL = [Drawing.Color]::FromArgb(255,197,49); $GRN = [Drawing.Color]::FromArgb(43,214,123)
$RED = [Drawing.Color]::FromArgb(255,77,77); $WHT = [Drawing.Color]::White
$GRY = [Drawing.Color]::FromArgb(150,158,170)

function New-Canvas($w=1920,$h=1080){
  $bmp = New-Object Drawing.Bitmap $w,$h
  $g = [Drawing.Graphics]::FromImage($bmp)
  $g.SmoothingMode='AntiAlias'; $g.TextRenderingHint='AntiAliasGridFit'
  $g.Clear($INK); return @($bmp,$g)
}
function Font($size,$bold=$true,$face="Segoe UI"){ $st = if($bold){[Drawing.FontStyle]::Bold}else{[Drawing.FontStyle]::Regular}; New-Object Drawing.Font $face,$size,$st,([Drawing.GraphicsUnit]::Pixel) }
function Text($g,$s,$size,$color,$x,$y,$align='Near',$bold=$true,$face="Segoe UI",$w=0){
  $f = Font $size $bold $face; $b = New-Object Drawing.SolidBrush $color
  $fmt = New-Object Drawing.StringFormat; $fmt.Alignment=$align
  if($w -gt 0){ $g.DrawString($s,$f,$b,(New-Object Drawing.RectangleF $x,$y,$w,2000),$fmt) } else { $g.DrawString($s,$f,$b,[single]$x,[single]$y,$fmt) }
}
function Box($g,$color,$x,$y,$w,$h){ $g.FillRectangle((New-Object Drawing.SolidBrush $color),$x,$y,$w,$h) }
function Brand($g){ Text $g "MARGIN MECHANICS" 26 $GRY 80 1010 'Near' $true }
function Save($pair,$name){ $pair[0].Save((Join-Path $vis $name),[Drawing.Imaging.ImageFormat]::Png); $pair[1].Dispose(); $pair[0].Dispose() }
function Bars($g,$items,$max,$top=330,$base=900,$left=360,$barW=420,$gap=260){
  $i=0; foreach($it in $items){
    $x = $left + $i*($barW+$gap); $h = [int](($base-$top)*$it.v/$max)
    Box $g $it.c $x ($base-$h) $barW $h
    Text $g $it.label 64 $WHT ($x+$barW/2) ($base-$h-90) 'Center'
    Text $g $it.name 38 $GRY ($x+$barW/2) ($base+25) 'Center' $false
    $i++ }
  $g.DrawLine((New-Object Drawing.Pen $GRY,3),200,$base,1720,$base)
}

# 01 hook
$c = New-Canvas; $g=$c[1]
Text $g "COSTCO FY2025 SALES" 48 $GRY 960 260 'Center'
Text $g '$270 BILLION' 190 $YEL 960 330 'Center' $true "Arial Black"
Text $g "...and the products aren't where the profit is." 60 $WHT 960 650 'Center' $false
Brand $g; Save $c "01_hook.png"

# 02 fees vs profit
$c = New-Canvas; $g=$c[1]
Text $g "A plastic card vs. the whole company" 64 $WHT 960 90 'Center'
Text $g "Costco, fiscal 2025" 38 $GRY 960 180 'Center' $false
Bars $g @(@{v=5.323;label='$5.3B';name='Membership fees';c=$YEL},@{v=8.099;label='$8.1B';name='Total net income';c=$GRN}) 8.099
Text $g "Source: Costco FY2025 Form 10-K" 26 $GRY 1840 1010 'Far' $false
Brand $g; Save $c "02_fees_vs_profit.png"

# 03 two models
$c = New-Canvas; $g=$c[1]
Text $g "TWO WAYS TO RUN A STORE" 64 $WHT 960 90 'Center'
Box $g $PANEL 140 240 780 680; Box $g $PANEL 1000 240 780 680
Box $g $GRY 140 240 780 16; Box $g $YEL 1000 240 780 16
Text $g "NORMAL RETAILER" 54 $GRY 530 300 'Center'
Text $g "COSTCO" 54 $YEL 1390 300 'Center'
Text $g "Buy product`nMark it up`nProfit on every item" 50 $WHT 530 450 'Center' $false
Text $g "Sell near cost`nCharge to get in`nProfit on membership" 50 $WHT 1390 450 'Center' $false
Text $g "Profit = the shelf" 44 $GRY 530 800 'Center'
Text $g "Profit = the card" 44 $GRN 1390 800 'Center'
Brand $g; Save $c "03_two_models.png"

# 04 fee growth
$c = New-Canvas; $g=$c[1]
Text $g "Membership fee income: +10% in one year" 64 $WHT 960 90 'Center'
Text $g "Fee hike Sept 2024: Gold Star `$60 > `$65 · Executive `$120 > `$130" 38 $GRY 960 180 'Center' $false
Bars $g @(@{v=4.828;label='$4.83B';name='FY2024';c=$GRY},@{v=5.323;label='$5.32B';name='FY2025';c=$YEL}) 5.323
Text $g "Source: Costco FY2025 Form 10-K" 26 $GRY 1840 1010 'Far' $false
Brand $g; Save $c "04_fee_growth.png"

# 05 renewal
$c = New-Canvas; $g=$c[1]
Text $g "MEMBERS WHO RENEW" 64 $WHT 960 110 'Center'
Text $g "92.3%" 220 $GRN 530 330 'Center' $true "Arial Black"
Text $g "US & Canada" 48 $GRY 530 640 'Center' $false
Text $g "89.8%" 220 $YEL 1390 330 'Center' $true "Arial Black"
Text $g "Worldwide" 48 $GRY 1390 640 'Center' $false
Text $g "Fiscal 2025 year-end · Source: Costco FY2025 results" 30 $GRY 960 820 'Center' $false
Brand $g; Save $c "05_renewal.png"

# 06 markup cap
$c = New-Canvas; $g=$c[1]
Text $g "THE MARKUP CAP" 72 $WHT 960 110 'Center'
Text $g "~14%" 200 $YEL 530 320 'Center' $true "Arial Black"
Text $g "Name brands" 48 $GRY 530 600 'Center' $false
Text $g "~15%" 200 $YEL 1390 320 'Center' $true "Arial Black"
Text $g "Kirkland Signature" 48 $GRY 1390 600 'Center' $false
Text $g "Low prices > membership pays for itself > members renew > profit" 44 $GRN 960 790 'Center'
Text $g "Widely reported Costco pricing practice" 26 $GRY 1840 1010 'Far' $false
Brand $g; Save $c "06_markup.png"

# 07 flywheel
$c = New-Canvas; $g=$c[1]
Text $g "THE COSTCO FLYWHEEL" 64 $WHT 960 60 'Center'
$steps = @(@{t="Low prices";x=730;y=190},@{t="More members";x=1240;y=480},@{t="More buying power";x=730;y=770},@{t="Even lower prices";x=220;y=480})
$pen = New-Object Drawing.Pen $YEL,10; $pen.CustomEndCap = New-Object Drawing.Drawing2D.AdjustableArrowCap 5,5
$g.DrawLine($pen,1190,300,1370,470); $g.DrawLine($pen,1370,620,1190,790)
$g.DrawLine($pen,730,790,550,620); $g.DrawLine($pen,550,470,730,300)
foreach($s in $steps){ Box $g $PANEL $s.x $s.y 460 130; Box $g $YEL $s.x $s.y 10 130; Text $g $s.t 44 $WHT ($s.x+235) ($s.y+38) 'Center' }
Text $g "MEMBERSHIP`nFEES" 52 $GRN 960 560 'Center'
Brand $g; Save $c "07_flywheel.png"

# Thumbnail 1280x720
$c = New-Canvas 1280 720; $g=$c[1]
Box $g $YEL 0 0 1280 14
Text $g "NOT THE" 120 $WHT 60 120 'Near' $true "Arial Black"
Text $g "GROCERIES" 120 $YEL 60 270 'Near' $true "Arial Black"
Text $g "Costco's real money machine" 44 $GRY 66 460 'Near' $false
# membership card
$path = New-Object Drawing.Drawing2D.GraphicsPath; $r=30; $cx=820; $cy=430; $cw=400; $ch=240
$path.AddArc($cx,$cy,$r,$r,180,90); $path.AddArc($cx+$cw-$r,$cy,$r,$r,270,90); $path.AddArc($cx+$cw-$r,$cy+$ch-$r,$r,$r,0,90); $path.AddArc($cx,$cy+$ch-$r,$r,$r,90,90); $path.CloseFigure()
$g.FillPath((New-Object Drawing.SolidBrush $WHT),$path)
Box $g $RED $cx ($cy+40) $cw 50
Text $g "MEMBER" 40 $INK ($cx+30) ($cy+130) 'Near'
Text $g '$5.3B' 110 $GRN 1240 120 'Far' $true "Arial Black"
$c[0].Save((Join-Path $Out "thumbnail.png"),[Drawing.Imaging.ImageFormat]::Png); $g.Dispose(); $c[0].Dispose()
"Done: $Out"
