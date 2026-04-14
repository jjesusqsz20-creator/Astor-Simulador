
$lines = Get-Content Astor.py -Encoding UTF8
for ($i = 0; $i -lt $lines.Length; $i++) {
    if ($i -ge 1590 -and $i -le 2465) {
        $lines[$i] = "    " + $lines[$i]
    }
}
$lines | Set-Content Astor.py -Encoding UTF8
