"""Use the packaged PNG renderer with the PDF exported by Microsoft Word.

The packaged LibreOffice conversion failed because LibreOffice is not bundled on
this Windows host. Word itself exports the saved DOCX; Poppler renders that PDF.
"""
from pathlib import Path
import importlib.util,os
R=Path(__file__).resolve().parent
package=Path('C:/Users/dakshant/.codex/plugins/cache/openai-primary-runtime/documents/26.921.10847/skills/documents/render_docx.py')
spec=importlib.util.spec_from_file_location('packaged_docx_renderer',package);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
poppler='C:/Users/dakshant/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/Library/bin'
os.environ['PATH']=poppler+os.pathsep+os.environ['PATH']
mod.convert_to_pdf=lambda *args,**kwargs:(str(R/'CookRisk_StageB_Final_Report.pdf'),'PDF exported directly by Microsoft Word')
paths=mod.rasterize(str(R/'CookRisk_StageB_Final_Report.docx'),str(R/'qa'),120,False,False)
print('Rendered',len(paths),'Word-exported pages using packaged Poppler workflow')
