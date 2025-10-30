<#
.SYNOPSIS
Renames a Python package (both .whl and .tar.gz) to a new name and rebuilds.

.EXAMPLE
.\RenamePythonPackage.ps1 -PackageDir "D:\Python\log02\EALogger" -OldName "alanlogger" -NewName "elLogger"
#>

param(
    [Parameter(Mandatory = $true)]
    [string]$PackageDir,

    [Parameter(Mandatory = $true)]
    [string]$OldName,

    [Parameter(Mandatory = $true)]
    [string]$NewName
)

$ErrorActionPreference = "Stop"
Set-Location $PackageDir

# Find files
$whlFile = Get-ChildItem "$OldName-*.whl" | Select-Object -First 1
$tarFile = Get-ChildItem "$OldName-*.tar.gz" | Select-Object -First 1

if (-not $whlFile) { throw "No wheel file found for $OldName" }
Write-Host ">>> Found wheel: $($whlFile.Name)"
if ($tarFile) { Write-Host ">>> Found source tarball: $($tarFile.Name)" }

# Extract version
if ($whlFile.Name -match "$OldName-(?<version>[\d\.]+)") {
    $version = $Matches.version
} else {
    throw "Could not extract version from wheel filename."
}
Write-Host ">>> Detected version: $version"

# --- Extract the wheel ---
$workDir = Join-Path $PackageDir "${NewName}_work"
if (Test-Path $workDir) { Remove-Item $workDir -Recurse -Force }
New-Item -ItemType Directory -Path $workDir | Out-Null

Write-Host ">>> Extracting wheel contents..."
python -m zipfile -e $whlFile.FullName $workDir

# --- Rename package folder and metadata ---
$distInfo = Get-ChildItem $workDir -Directory | Where-Object { $_.Name -like "*.dist-info" }
if (-not $distInfo) { throw "No .dist-info folder found!" }

$oldPackageDir = Join-Path $workDir $OldName
$newPackageDir = Join-Path $workDir $NewName
if (Test-Path $oldPackageDir) {
    Write-Host ">>> Renaming code folder $OldName → $NewName"
    Rename-Item $oldPackageDir $newPackageDir
}

$newDistInfoDir = Join-Path $workDir "$NewName-$version.dist-info"
Rename-Item $distInfo.FullName $newDistInfoDir

$metaFile = Join-Path $newDistInfoDir "METADATA"
(Get-Content $metaFile) -replace "Name:\s*$OldName", "Name: $NewName" | Set-Content $metaFile

# --- Repack wheel ---
Write-Host ">>> Rebuilding wheel..."
pip install wheel | Out-Null
Set-Location $workDir
python -m wheel pack . -d ..

# --- Clean up ---
Set-Location $PackageDir
$newWheel = "$PackageDir\$NewName-$version-py3-none-any.whl"
Write-Host ">>> ✅ New wheel created: $newWheel"

# --- Handle source tarball (.tar.gz) if present ---
if ($tarFile) {
    $srcWorkDir = Join-Path $PackageDir "${NewName}_src"
    if (Test-Path $srcWorkDir) { Remove-Item $srcWorkDir -Recurse -Force }
    New-Item -ItemType Directory -Path $srcWorkDir | Out-Null

    Write-Host ">>> Extracting source tarball..."
    tar -xzf $tarFile.FullName -C $srcWorkDir

    $srcPkgFolder = Join-Path $srcWorkDir "$OldName-$version"
    $newSrcPkgFolder = Join-Path $srcWorkDir "$NewName-$version"
    Rename-Item $srcPkgFolder $newSrcPkgFolder

    # Update metadata in setup.cfg or pyproject.toml if found
	$setupCfg = Join-Path $newSrcPkgFolder "setup.cfg"
	if (Test-Path $setupCfg) {
		(Get-Content $setupCfg) -replace ("name\s*=\s*" + $OldName), ("name = " + $NewName) | Set-Content $setupCfg
	}
	$pyproject = Join-Path $newSrcPkgFolder "pyproject.toml"
	if (Test-Path $pyproject) {
		(Get-Content $pyproject) -replace ('name\s*=\s*"' + $OldName + '"'), ('name = "' + $NewName + '"') | Set-Content $pyproject
	}

    Write-Host ">>> Repacking source tarball..."
    tar -czf "$PackageDir\$NewName-$version.tar.gz" -C $srcWorkDir "$NewName-$version"
    Write-Host ">>> ✅ New tarball created: $PackageDir\$NewName-$version.tar.gz"
}

Write-Host "`n>>> All done! Install it with:"
Write-Host "    pip install --upgrade `"$newWheel`""
