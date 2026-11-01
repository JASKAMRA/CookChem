from build import *
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak,Flowable
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from xml.sax.saxutils import escape
S=getSampleStyleSheet();S.add(ParagraphStyle(name='BodyCook',fontName='Helvetica',fontSize=9.3,leading=13,spaceAfter=7,textColor=colors.HexColor('#213247')));S.add(ParagraphStyle(name='CellCook',fontSize=8,leading=10,textColor=colors.HexColor('#213247')))
S['Title'].textColor=colors.HexColor('#12384b');S['Heading1'].textColor=colors.HexColor('#12384b');S['Heading1'].fontSize=17;S['Heading2'].textColor=colors.HexColor('#146d73');S['Heading2'].fontSize=11
def P(t,style='BodyCook'):return Paragraph(t,S[style])
def table(rows,widths):
 t=Table([[P(escape(str(c)),'CellCook') for c in r] for r in rows],colWidths=widths,repeatRows=1,hAlign='LEFT');t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e0eeef')),('VALIGN',(0,0),(-1,-1),'TOP'),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5),('LINEBELOW',(0,0),(-1,0),1,colors.HexColor('#146d73')),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#f5f7f9')]) ]));return t
class Process(Flowable):
 def __init__(self):Flowable.__init__(self);self.width=480;self.height=130
 def draw(self):
  c=self.canv;labels=['Inspect attempt + freeze V6','Search + screen primary sources','Resolve reference identity','Extract scoped claims + nulls','Audit issues + validate V7','Report + checksum archive'];w=151;h=44
  for i,l in enumerate(labels):
   col=i%3;row=i//3;x=col*165;y=77-row*69;c.setFillColor(colors.HexColor('#e0eeef'));c.setStrokeColor(colors.HexColor('#146d73'));c.roundRect(x,y,w,h,5,fill=1);c.setFillColor(colors.HexColor('#12384b'));c.setFont('Helvetica',8);words=l.split();mid=len(words)//2;c.drawCentredString(x+w/2,y+26,' '.join(words[:mid]));c.drawCentredString(x+w/2,y+14,' '.join(words[mid:]))
   if col<2:c.line(x+w,y+h/2,x+164,y+h/2);c.line(x+160,y+h/2+3,x+164,y+h/2);c.line(x+160,y+h/2-3,x+164,y+h/2)
  c.line(404,77,404,61);c.line(404,61,74,61);c.line(74,61,74,52);c.line(71,55,74,52);c.line(77,55,74,52)
