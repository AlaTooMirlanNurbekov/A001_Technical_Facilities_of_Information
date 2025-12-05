# For those who may not know: a .ps1 file is simply a powerShell script. it is when normal text file that contains
# commands powerShell can run. It is built into Windows and is often used by system administrators to automate tasks, read logs, manage computers and perform quick system checks. 
# You can open .ps1 files in any text editor, look at the commands, and run them in PowerShell just like you would run a program.
# This script reads a firewall log and lets you explore the entries.

param(
    [string]$LogPath = ".\firewall.log"
)

Write-Host "=== TFI03 – Firewall Log Reader ===`n"
Write-Host "Log file path: $LogPath`n"

if (-not (Test-Path -Path $LogPath)) {
    Write-Host "[!] Log file not found. Create 'firewall.log' in this folder or pass a path with -LogPath."
    exit 1
}

#read raw lines
$lines = Get-Content -Path $LogPath | Where-Object { $_.Trim() -ne "" }

if ($lines.Count -eq 0) {
    Write-Host "[!] Log file is empty."
    exit 0
}

#simple parser for the expected format
function Parse-FirewallLine {
    param(
        [string]$Line
    )

    # split on spaces first
    $parts = $Line.Split(" ", [System.StringSplitOptions]::RemoveEmptyEntries)

    if ($parts.Count -lt 6) {
        return $null
    }

    $date   = $parts[0]
    $time   = $parts[1]
    $action = $parts[2] # ALLOW / BLOCK
    $proto  = $parts[3]  # TCP / UDP / etc.

    # source:port is at index 4 "ip:port"
    $src    = $parts[4]
    # "->" should be at index 5
    # destination:port is at index 6 (if present)
    $dst    = $null
    if ($parts.Count -ge 7) {
        $dst = $parts[6]
    }

    # Extract just IP part from "ip:port"
    $srcIp = $src.Split(":")[0]
    $dstIp = $dst.Split(":")[0]

    [PSCustomObject]@{
        DateTime = "$date $time"
        Action   = $action
        Protocol = $proto
        Source   = $src
        SourceIP = $srcIp
        Dest     = $dst
        DestIP   = $dstIp
        RawLine  = $Line
    }
}
$entries = foreach ($line in $lines) {
    $e = Parse-FirewallLine -Line $line
    if ($null -ne $e) { $e }
}

if (-not $entries -or $entries.Count -eq 0) {
    Write-Host "[!] No valid entries were parsed from the log."
    exit 0
}

# Basic stats
$allowCount = ($entries | Where-Object { $_.Action -eq "ALLOW" }).Count
$blockCount = ($entries | Where-Object { $_.Action -eq "BLOCK" }).Count
$total      = $entries.Count

Write-Host "--- Summary ---"
Write-Host ("Total events : {0}" -f $total)
Write-Host ("Allowed      : {0}" -f $allowCount)
Write-Host ("Blocked      : {0}" -f $blockCount)

#Top 5 source IPs by number of blocked events
$topBlocked = $entries |
    Where-Object { $_.Action -eq "BLOCK" } |
    Group-Object -Property SourceIP |
    Sort-Object -Property Count -Descending |
    Select-Object -First 5

if ($topBlocked.Count -gt 0) {
    Write-Host "`nTop source IPs (BLOCK events):"
    foreach ($g in $topBlocked) {
        Write-Host ("  {0} : {1} blocked" -f $g.Name, $g.Count)
    }
}

#Simple interactive filter menu
while ($true) {
    Write-Host "`nMenu:"
    Write-Host "  1) Show last 10 events"
    Write-Host "  2) Show only BLOCK events"
    Write-Host "  3) Show only ALLOW events"
    Write-Host "  4) Filter by source IP"
    Write-Host "  5) Exit"

    $choice = Read-Host "Choose an option (1-5)"

    switch ($choice) {
        "1" {
            Write-Host "`nLast 10 events:"
            $entries | Select-Object -Last 10 | ForEach-Object {
                Write-Host $_.RawLine
            }
        }
        "2" {
            Write-Host "`nBLOCK events:"
            $entries | Where-Object { $_.Action -eq "BLOCK" } | ForEach-Object {
                Write-Host $_.RawLine
            }
        }
        "3" {
            Write-Host "`nALLOW events:"
            $entries | Where-Object { $_.Action -eq "ALLOW" } | ForEach-Object {
                Write-Host $_.RawLine
            }
        }
        "4" {
            $ip = Read-Host "Enter source IP"
            if ([string]::IsNullOrWhiteSpace($ip)) {
                continue
            }

            $filtered = $entries | Where-Object { $_.SourceIP -eq $ip }
            if ($filtered.Count -eq 0) {
                Write-Host "No entries found for source IP $ip"
            }
            else {
                Write-Host "`nEntries from $ip:"
                $filtered | ForEach-Object {
                    Write-Host $_.RawLine
                }
            }
        }
        "5" {
            Write-Host "Bye."
            break
        }
        Default {
            Write-Host "[!] Invalid choice."
        }
    }
    if ($choice -eq "5") { break }
}