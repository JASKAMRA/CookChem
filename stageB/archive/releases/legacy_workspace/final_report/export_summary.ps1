$ErrorActionPreference = 'Stop'
$reportPath = 'C:\Users\dakshant\Documents\CookChem\stageB\final_report\CookRisk_StageB_Summary_Report.docx'
$pdfPath = 'C:\Users\dakshant\Documents\CookChem\stageB\final_report\CookRisk_StageB_Summary_Report.pdf'
$reportWord = New-Object -ComObject Word.Application
$reportOwnInstance = $reportWord.Documents.Count -eq 0
if (-not $reportOwnInstance) { throw 'Existing Word documents detected; do not change the user session.' }
$reportWord.Visible = $false
$reportWord.DisplayAlerts = 0
$reportWord.AutomationSecurity = 3
$reportDocument = $null
try {
    $reportDocument = $reportWord.Documents.Open($reportPath, $false, $false)
    $reportDocument.Fields.Update() | Out-Null
    foreach ($reportToc in $reportDocument.TablesOfContents) { $reportToc.Update() }
    $reportDocument.Repaginate()
    foreach ($reportToc in $reportDocument.TablesOfContents) { $reportToc.UpdatePageNumbers() }
    $reportDocument.Save()
    $reportDocument.ExportAsFixedFormat($pdfPath, 17)
    Write-Output "Exported PDF with $($reportDocument.ComputeStatistics(2)) Word pages"
} finally {
    if ($null -ne $reportDocument) { $reportDocument.Close(0) }
    if ($reportOwnInstance) { $reportWord.Quit() }
    [System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($reportWord) | Out-Null
}
