# --- CONFIGURATION ---
$ErrorActionPreference = "Stop"

$OutFiles = @(
    "full_project_context.md"
)

# Extensions that should NOT be concatenated (binary files)
$BinaryExtensions = @(
    ".pdf", ".png", ".jpg", ".jpeg", ".gif",
    ".exe", ".dll", ".zip", ".7z",
    ".mp4", ".mp3", ".wav", ".avi",
    ".ico", ".bin"
)

# --- 1. ENVIRONMENT CHECK ---
try {
    if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
        throw "The 'git' command was not found. Make sure it is installed and in your PATH."
    }

    $isGitRepo = git rev-parse --is-inside-work-tree --quiet 2>$null
    if ($isGitRepo -ne "true") {
        throw "Not inside a Git repository."
    }
}
catch {
    Write-Host "Error: 'git' is not working or you are not inside a Git repository." -ForegroundColor Red
    exit 1
}

# --- 2. INITIALIZATION AND CONTENT BUILDING ---
Write-Host "Starting project concatenation process..." -ForegroundColor Green

$contentBuilder = [System.Text.StringBuilder]::new()

$null = $contentBuilder.AppendLine("## 1. PROJECT METADATA ##")
$null = $contentBuilder.AppendLine("Generation date: $(Get-Date)")
$null = $contentBuilder.AppendLine("Project directory: $((Get-Location).Path)")
$null = $contentBuilder.AppendLine("Current commit: $(git rev-parse --short HEAD)")
$null = $contentBuilder.AppendLine()
$null = $contentBuilder.AppendLine("## 2. FULL FILE STRUCTURE ##")

$allFiles = git ls-files -c --others --exclude-standard

if (Get-Command tree -ErrorAction SilentlyContinue) {
    $null = $contentBuilder.AppendLine("(Displaying the full directory tree, as Windows 'tree' lacks --fromfile)")
    $treeOutput = tree /F /A | Out-String
    $null = $contentBuilder.Append($treeOutput)
}
else {
    foreach ($line in $allFiles) {
        $null = $contentBuilder.AppendLine($line)
    }
}

$null = $contentBuilder.AppendLine()
$null = $contentBuilder.AppendLine("## 3. CONTENT OF ALL FILES ##")

foreach ($file in $allFiles) {

    # Normalize Git paths to Windows paths
    $file = $file -replace '/', '\'

    # Skip output files
    if ($OutFiles -contains $file) { continue }

    # Skip this script itself
    if ($MyInvocation.MyCommand.Name -eq $file) { continue }

    # Skip binary files
    $extension = [IO.Path]::GetExtension($file).ToLower()
    if ($BinaryExtensions -contains $extension) {
        Write-Host "  -> Skipping binary file: $file" -ForegroundColor DarkYellow
        continue
    }

    if (Test-Path -LiteralPath $file -PathType Leaf) {
        Write-Host "  -> Processing: $file"

        try {
            $fileText = Get-Content -LiteralPath $file -Raw -ErrorAction Stop

            $null = $contentBuilder.AppendLine("--- START OF FILE: $file ---")
            $null = $contentBuilder.AppendLine($fileText)
            $null = $contentBuilder.AppendLine("--- END OF FILE: $file ---")
            $null = $contentBuilder.AppendLine()
        }
        catch {
            Write-Host "  !! Failed to read file: $file" -ForegroundColor Red
        }
    }
}

# --- 3. WRITING TO OUTPUT FILES ---
$finalContent = $contentBuilder.ToString()

foreach ($outFile in $OutFiles) {
    Write-Host "  -> Writing to output file: $outFile" -ForegroundColor Cyan
    Set-Content -LiteralPath $outFile -Value $finalContent -Encoding UTF8
}

Write-Host "-------------------------------------------------"
Write-Host "Process completed. Output files generated:" -ForegroundColor Green
$OutFiles.ForEach({ Write-Host " - $_" })

PAUSE

