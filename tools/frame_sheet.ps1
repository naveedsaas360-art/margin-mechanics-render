# Contact sheet of N evenly spaced frames from a local MP4, using built-in Windows media APIs.
param([Parameter(Mandatory)][string]$Video, [int]$Count = 48, [string]$Out = "")
Add-Type -AssemblyName System.Runtime.WindowsRuntime, System.Drawing
$null = [Windows.Storage.StorageFile, Windows.Storage, ContentType = WindowsRuntime]
$null = [Windows.Media.Editing.MediaComposition, Windows.Media.Editing, ContentType = WindowsRuntime]
$null = [Windows.Graphics.Imaging.BitmapDecoder, Windows.Graphics.Imaging, ContentType = WindowsRuntime]
$asTask = [System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object {
  $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1' }
function Await($op, [Type]$t) { $task = $asTask.MakeGenericMethod($t).Invoke($null, @($op)); $task.Wait(-1) | Out-Null; $task.Result }

$file = Await ([Windows.Storage.StorageFile]::GetFileFromPathAsync((Resolve-Path $Video).Path)) ([Windows.Storage.StorageFile])
$clip = Await ([Windows.Media.Editing.MediaClip]::CreateFromFileAsync($file)) ([Windows.Media.Editing.MediaClip])
$comp = New-Object Windows.Media.Editing.MediaComposition; ([System.Collections.Generic.IList[Windows.Media.Editing.MediaClip]]$comp.Clips).Add($clip)
$total = $clip.OriginalDuration.TotalSeconds
$cols = 6; $tw = 320; $th = 180; $rows = [math]::Ceiling($Count / $cols)
$sheet = New-Object Drawing.Bitmap ($cols*$tw), ($rows*($th+22)); $g = [Drawing.Graphics]::FromImage($sheet); $g.Clear([Drawing.Color]::White)
$font = New-Object Drawing.Font "Segoe UI",11,([Drawing.FontStyle]::Bold)
for($i=0; $i -lt $Count; $i++){
  $t = $total * ($i + 0.5) / $Count
  $stream = Await ($comp.GetThumbnailAsync([TimeSpan]::FromSeconds($t), $tw, $th, [Windows.Media.Editing.VideoFramePrecision]::NearestFrame)) ([Windows.Graphics.Imaging.ImageStream])
  $net = [System.IO.WindowsRuntimeStreamExtensions]::AsStreamForRead($stream)
  $img = [Drawing.Image]::FromStream($net)
  $x = ($i % $cols) * $tw; $y = [math]::Floor($i / $cols) * ($th+22)
  $g.DrawImage($img, $x, $y, $tw-4, $th); $img.Dispose(); $net.Dispose()
  $g.DrawString(("{0}:{1:00}" -f [math]::Floor($t/60), [math]::Floor($t%60)), $font, [Drawing.Brushes]::Black, $x+4, $y+$th+2)
}
if(-not $Out){ $Out = [IO.Path]::ChangeExtension($Video, ".sheet.jpg") }
$sheet.Save($Out, [Drawing.Imaging.ImageFormat]::Jpeg); "saved $Out  (duration $([math]::Round($total,1)) s)"
