from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.text import WD_ALIGN_PARAGRAPH

O=Path(__file__).resolve().parent
im=Image.new('RGB',(1800,1665),'white');draw=ImageDraw.Draw(im)
bold=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',28)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',23)
def xy(x,y):return (int(x*180),int((10-y)*166.5))
def label(x,y,t,f):draw.text(xy(x,y),t,font=f,fill='black',anchor='mm',align='center',spacing=10)
nodes=[(5,9.25,'Preserve inputs and review Stage A context','Master CSV, saved OOF predictions and background reports'),(5,7.8,'Inventory and verify chemical identity','198 molecular groups; retain unresolved identities separately'),(5,6.35,'Prioritize compounds and search primary literature','Initial inventory search followed by nine compound expansion'),(5,4.9,'Screen and extract measured interaction evidence','Dose, population, preparation, direction, outcome and source'),(2.45,3.35,'Interaction evidence','33 initial records → 64 final records'),(7.55,3.35,'Separate processing evidence','3 records kept outside interaction count'),(5,1.75,'Validate and package the evidence release','Check identifiers, source traceability, conflicts and output files')]
for x,y,t,s in nodes:
    w=8.9 if x==5 else 4.65
    draw.rounded_rectangle([xy(x-w/2,y+.48),xy(x+w/2,y-.48)],radius=18,fill='#F2F5F7',outline='#536573',width=3)
    label(x,y+.13,t,bold);label(x,y-.19,s,font)
def arrow(a,b):
    import math
    start,end=xy(*a),xy(*b);draw.line([start,end],fill='#536573',width=4)
    angle=math.atan2(end[1]-start[1],end[0]-start[0])
    draw.polygon([end,(end[0]-18*math.cos(angle-.5),end[1]-18*math.sin(angle-.5)),(end[0]-18*math.cos(angle+.5),end[1]-18*math.sin(angle+.5))],fill='#536573')
for top,bottom in [(9.25,7.8),(7.8,6.35),(6.35,4.9)]:arrow((5,top-.52),(5,bottom+.52))
for x in [2.45,7.55]:arrow((5,4.38),(x,3.87));arrow((x,2.83),(5,2.27))
label(5,.53,'Saved Stage A linkage provides context for the initial release.\nExposure estimation and clinical risk assessment remain future stages.',font)
im.save(O/'stageB_process_flowchart.png')

d=Document();sec=d.sections[0];sec.page_width=Inches(8.5);sec.page_height=Inches(11)
sec.top_margin=sec.bottom_margin=Inches(.7);sec.left_margin=sec.right_margin=Inches(.75)
for name in ['Normal','Title','Heading 1','Heading 2']:
    st=d.styles[name];st.font.name='Calibri';st.font.color.rgb=RGBColor(0,0,0)
    for b in list(st.element.xpath('./w:pPr/w:pBdr')):b.getparent().remove(b)
normal=d.styles['Normal'];normal.font.size=Pt(11);normal.paragraph_format.space_after=Pt(7);normal.paragraph_format.line_spacing=1.08
d.styles['Title'].font.size=Pt(24);d.styles['Heading 1'].font.size=Pt(16);d.styles['Heading 2'].font.size=Pt(12)
footer=sec.footer.paragraphs[0];footer.alignment=WD_ALIGN_PARAGRAPH.RIGHT
footer.add_run('CookRisk Stage B Summary  |  ')
for label,instr in [('', 'PAGE'),(' of ', 'NUMPAGES')]:
    footer.add_run(label);f=OxmlElement('w:fldSimple');f.set(qn('w:instr'),instr);footer._p.append(f)
for r in footer.runs:r.font.size=Pt(9)
def p(t):d.add_paragraph(t)
def h(t):d.add_heading(t,level=2)
def page(t):d.add_page_break();d.add_heading(t,level=1)
def table(headers,rows,widths):
    t=d.add_table(rows=1,cols=len(headers));t.autofit=False
    for c,w in zip(t.columns,widths):c.width=Inches(w)
    for c,s in zip(t.rows[0].cells,headers):c.text=s
    for row in rows:
        for c,s in zip(t.add_row().cells,row):c.text=str(s)
    for i,row in enumerate(t.rows):
        pr=row._tr.get_or_add_trPr();pr.append(OxmlElement('w:cantSplit'))
        if i==0:pr.append(OxmlElement('w:tblHeader'))
        for c,w in zip(row.cells,widths):
            c.width=Inches(w);cp=c._tc.get_or_add_tcPr();sh=OxmlElement('w:shd');sh.set(qn('w:fill'),'333333' if i==0 else ('F2F3F4' if i%2 else 'FFFFFF'));cp.append(sh)
            bd=OxmlElement('w:tcBorders')
            for edge in ['top','left','bottom','right']:
                b=OxmlElement('w:'+edge);b.set(qn('w:val'),'single');b.set(qn('w:sz'),'4');b.set(qn('w:color'),'D9D9D9');bd.append(b)
            cp.append(bd);m=OxmlElement('w:tcMar')
            for edge in ['top','left','bottom','right']:
                b=OxmlElement('w:'+edge);b.set(qn('w:w'),'85');b.set(qn('w:type'),'dxa');m.append(b)
            cp.append(m)
            for para in c.paragraphs:
                para.paragraph_format.space_after=Pt(2);para.paragraph_format.space_before=Pt(2)
                for r in para.runs:r.font.size=Pt(10);r.font.bold=i==0;r.font.color.rgb=RGBColor(255,255,255) if i==0 else RGBColor(0,0,0)
    d.add_paragraph().paragraph_format.space_after=Pt(0)

d.add_paragraph('CookRisk Stage B Summary Report','Title')
p('Key methods, findings and deliverables from the initial release and expanded release v2')
h('Purpose and main outcome')
p('CookRisk studies how cooking changes food compounds and how those compounds may interact with drugs. Stage B built a traceable literature evidence layer to support later integration with compound retention and exposure. The final release contains 64 evidence records across nine compounds and 34 drugs or probe drugs, supported by 45 primary reports.')
p('The expansion added 31 records to the original 33 while preserving source references, null findings, preparation differences and context dependent results. Stage B is complete as a bounded evidence release. It does not establish a clinically validated risk score for cooked meals.')
table(['Measure','Initial release','Final release'],[['Evidence records',33,64],['Anchor compounds',5,9],['Drugs and probe drugs',18,34],['Primary reports',26,45]], [3.4,1.8,1.8])
h('What was completed')
p('We preserved the supplied data, checked molecular identities, searched and screened primary literature, extracted interaction evidence, separated cooking studies, audited source provenance and validated the release. The original Stage B outputs remain available alongside the expanded tables.')
h('Where Stage B fits')
p('Stage A supplies retention predictions. Stage B supplies documented interaction evidence. Stage C must translate retained amounts into credible exposure estimates; a later risk stage must validate the clinical interpretation. No retention model was retrained and no new exposure or clinical risk predictions were generated.')

page('Stage B process flowchart')
p('The workflow connects identity verification with primary evidence extraction and release validation. Processing evidence follows a separate branch so cooking outcomes are not counted as drug interaction experiments.')
d.add_picture(str(O/'stageB_process_flowchart.png'),width=Inches(6.9))
p('Figure 1  Process followed for the initial release and the focused expansion. The evidence layer remains independent of the choice of Stage A prediction model.')

page('Methods evidence coverage and final outputs')
h('Inputs and identity checks')
p('The master dataset contained 1,350 observations, 97 columns and 198 nonblank molecular groups. The 221 observations without a molecular group identifier were retained separately. Saved Stage A predictions and the supplied benchmark and literature reports provided project context; input copies and hashes were preserved.')
p('PubChem information and structure comparison supported 79 exact mappings and 23 parent connectivity mappings; 96 groups remained uncertain. A later QC overlay also excluded mixed ascorbic acid measurements, giving 97 excluded or uncertain groups in the expansion priority table. Parent mappings carry stereochemical restrictions and do not prove isomer specific exposure.')
h('Literature search and screening')
p('The initial inventory search was followed by 45 logged expansion queries for nine compounds, using Europe PMC, primary PubMed or PMC checking and Crossref metadata checks through 6 October 2026. Inclusion required reliable identity, a traceable primary report and a measured drug or probe effect or tested null. Retrieval caps and incomplete screening limit coverage; this is not an exhaustive systematic review.')
h('Evidence extraction')
p('The 36 field evidence table preserves preparation, dose, population, endpoints, direction, mechanisms and source limitations. Its 64 rows are not 64 independent trials or proven hazards: rows can share a primary report. Metabolic ratios, assays and drug exposure measures remain distinct; disputed numbers were withheld.')
table(['Evidence coverage','Records'],[['Human pharmacokinetic and controlled clinical','49 + 2 = 51'],['Animal and in vitro','7 + 6 = 13'],['With quantitative outcomes','42 of 64']], [5.2,1.8])
h('Validation')
p('The initial release passed 20 checks and the expansion passed 13 for identifiers, counts, relationships and source traceability. Among 208 inherited dataset DOIs, 145 had author or year discrepancies, 10 were unavailable and 53 had concordant metadata. Flags require review rather than proving every measurement false; primary interaction reports were audited separately.')
h('Deliverables and Stage A linkage')
p('The main output is stageB/expansion_v2/outputs/stageB_food_drug_interactions_expanded.csv. Supporting files include study and drug registries, prioritization, identity QC, conflict synthesis, search and screening logs, source audits, caches and release archives. The full report supplies profiles and references.')
p('Saved Stage A OOF predictions cover 1,124 observations and 197 groups. All 33 initial evidence records linked to that inventory; this linkage was not rebuilt for all 64. An eligibility discrepancy affecting 115 OOF observations remains unresolved without the frozen training input.')

page('Key findings across the nine compounds')
p('The following are selected measured findings, not clinical risk ratings. AUC measures exposure; Cmax is peak concentration; GMR is a geometric mean ratio. Record counts include all retained contexts, not only human studies.')
h('Berberine 5 records')
p('A small renal transplant substudy reported cyclosporine AUC +34.5% and oral clearance −40.4%. Human midazolam AUC increased 40%. A ninefold dextromethorphan parent to metabolite ratio indicates lower CYP2D6 activity, not ninefold drug exposure. CYP3A and CYP2C9 probe effects were also captured.')
h('Piperine 13 records')
p('Small human studies reported increased exposure to propranolol, theophylline, phenytoin, carbamazepine, nevirapine, fexofenadine, chlorzoxazone and diclofenac. Selected results were carbamazepine AUC +47.9%, nevirapine AUC approximately +170%, and fexofenadine AUC 3403.7 to 5724.7 ng·h/mL. Proposed absorption, CYP and P-gp mechanisms vary by study; pepper soup and isolated piperine are different interventions.')
h('Curcumin 9 records')
p('Human endoxifen AUC changed −7.7% with curcumin alone (95% CI −15.4 to +0.7; p=0.07) and −12.4% with added piperine (−21.9 to −1.9; p=0.02). The combination cannot be attributed to curcumin alone. A curcuminoid/piperine mixture had no meaningful parent PK effect for midazolam, flurbiprofen or acetaminophen. Sulfasalazine exposure increased, with BCRP support; disputed numerical folds were withheld.')
h('EGCG 7 records')
p('Green tea extract reduced nadolol AUC, with GMRs 0.72 and 0.60 at two doses; this was not isolated EGCG. A single EGCG dose reduced rosuvastatin AUC (GMR 0.81), but its Cmax interval crossed 1 and 10 day pretreatment produced a null. Bortezomib antagonism was preclinical and concentration dependent; no human interaction was established.')
h('Caffeine 14 records and resveratrol 10 records')
p('Caffeine increased clozapine AUC 19% in one study. Reverse interactions were important: fluvoxamine and some quinolones reduced caffeine clearance. Resveratrol increased diclofenac AUC (GMR 2.12) and altered CYP probe measures, including buspirone AUC (GMR 1.33). Its methotrexate evidence remained preclinical. Supplement doses do not establish cooked food exposure.')
h('Genistein 3 records naringin 2 records and capsaicin 1 record')
p('Genistein changed caffeine metabolic indices and reduced midazolam and talinolol exposure, suggesting enzyme or transporter modulation. Isolated naringin reduced fexofenadine AUC to 75% of water control; the larger grapefruit juice effect was not attributed to naringin alone. Capsaicin 400 or 800 µg with aspirin 500 mg did not detectably alter platelet inhibition in 15 healthy men.')

page('Mechanisms conflicts cooking evidence and next steps')
h('Mechanisms captured')
p('Sources described CYP inhibition or induction, uptake and efflux transport, altered absorption or elimination, and pharmacodynamic augmentation or antagonism. Examples include berberine and resveratrol CYP probe effects, piperine CYP/P-gp pathways, curcumin BCRP inhibition, and EGCG or naringin OATP uptake inhibition. Genistein probe findings suggested both inhibition and induction. Bortezomib antagonism involved a proposed direct chemical reaction in preclinical work. Capturing a mechanism does not establish clinical causality.')
h('Five context dependent conflict groups')
p('Piperine with carbamazepine increased exposure in humans but decreased systemic and brain exposure under repeated rat dosing. Piperine with midazolam differed between an isolated compound study and a curcuminoid mixture null. Curcumin with tamoxifen increased rat exposure but reduced human exposure under different regimens. EGCG with bortezomib depended on preclinical concentration, while EGCG with rosuvastatin differed between a single dose and pretreatment. These are not same protocol contradictions and were not averaged.')
h('What null and missing evidence mean')
p('The mixture PK nulls, capsaicin aspirin platelet null and EGCG rosuvastatin pretreatment null apply only to their tested endpoints and conditions. Absence of a database row means no qualifying evidence was retained under the bounded search and identity policy; it does not establish absence of an interaction.')
h('Cooking and processing findings')
p('Three separate records from two publications reported piperine losses of approximately 16–34% and curcumin losses of 27–53%, or 12–30% with tamarind, under tested spice heating conditions. The spice study used boiling for 10 or 20 minutes and pressure cooking for 10 minutes. These are matrix specific observations rather than universal retention coefficients.')
p('Tea infusions at 60 °C or 95 °C for 5–300 minutes showed time and temperature dependent extraction and epimerization; total catechins peaked at 95 °C for 10 minutes. This is not isolated EGCG retention. None of these processing results establishes how cooking changes a drug interaction or clinical outcome.')
h('Stage C priorities and final interpretation')
p('Resolve identity and food measurement provenance issues, reconcile the Stage A eligibility discrepancy and rebuild expanded linkage. Exposure estimation requires compatible chemical forms, serving sizes, concentration units, retention values, timing and bioavailability. Supplement doses, cell concentrations and animal doses cannot simply be converted into a cooked serving.')
p('Stage B provides an auditable evidence foundation with human interaction signals, null findings and context dependent mechanisms. A clinical risk score or retained dose recommendation still requires exposure compatibility and independent validation.')
p('Source basis: the consolidated final report, saved evidence and study registry, and the supplied findings summary. Primary references remain in the full report and source identified CSV rows. No new studies or model predictions were generated for this revision.')

d.save(O/'CookRisk_StageB_Summary_Report.docx')
src=(O/'export_word.ps1').read_text();(O/'export_summary.ps1').write_text(src.replace('CookRisk_StageB_Final_Report','CookRisk_StageB_Summary_Report'))
src=(O/'render_report.py').read_text();(O/'render_summary.py').write_text(src.replace('CookRisk_StageB_Final_Report','CookRisk_StageB_Summary_Report').replace("str(R/'qa')","str(R/'summary_qa')"))
print('Created summary document and flowchart')
