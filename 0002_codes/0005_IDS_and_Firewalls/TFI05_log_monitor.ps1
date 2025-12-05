#This script monitors a text log file and highlights lines that look like INFO / WARNING / ERROR messages
#
# Expected example lines in the log:
#   [INFO] Service started
#   [WARN] High memory usage
#   [ERROR] Database connection failed
#
# You can manually append lines to test:
#   echo "[ERROR] Something went wrong" >> system.log

param(
    [string]$LogPath = ".\system.log"
)

Write-Host "=== TFI05 – Log Monitor ===`n"
Write-Host "Log file path: $LogPath`n"

#If the log file does not exist, create an empty one
if (-not (Test-Path -Path $LogPath)) {
    Write-Host "[INFO] Log file does not exist. Creating a new one..."
    New-Item -Path $LogPath -ItemType File -Force | Out-Null
}

Write-Host "[INFO] Monitoring log. Press Ctrl+C to stop.`n"

function Show-LogLine {
    param(
        [string]$Line
    )

    $trimmed = $Line.Trim()

    if ($trimmed -like "[ERROR]*") {
        # red for errors
        Write-Host $trimmed -ForegroundColor Red
    }
    elseif ($trimmed -like "[WARN]*") {
        #yellow for warnings
        Write-Host $trimmed -ForegroundColor Yellow
    }
    elseif ($trimmed -like "[INFO]*") {
        #green for info
        Write-Host $trimmed -ForegroundColor Green
    }
    else
        {
        # Default color for everything else
        Write-Host $trimmed
    }
}

try {
    # Follow the file as it grows (similar to `tail -f` on Linux)
    Get-Content -Path $LogPath -Wait -Tail 0 | ForEach-Object {
        if ($null -ne $_ -and $_.Trim() -ne "") {
            Show-LogLine -Line $_
        }
    }
}
catch {
    Write-Host "[!] An error occurred while reading the log:" -ForegroundColor Red
    Write-Host $_.Exception.Message
}
