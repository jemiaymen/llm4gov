for ($year = 2019; $year -le 2026; $year++) {
    # Check if the folder exists before adding it
    if (Test-Path -Path $year) {
        git add "$year/"
        git commit -m "add data $year"
        git push
        Write-Host "pushed folder: $year" -ForegroundColor Green
    } 
}

git add *
git commit -m "commit get_all_jort and git_add_script scripts"
git push