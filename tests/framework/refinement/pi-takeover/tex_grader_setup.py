"""TrustedUbuntuTeXrunner only;networkpublicpreloadthenunchangedofflinegrade."""
import pathlib,hashlib
R=pathlib.Path(__file__).resolve().parent
# ReuseexactvalidatedUbuntu/TLS/disconnectionlogic,removeunneededpandas only.
source=(R/'financial_grader_setup.py').read_text()
assert source.count(' -w pandas==2.3.2')==1 and source.count("'pandas':'2.3.2',")==1
source=source.replace(' -w pandas==2.3.2','').replace("'pandas':'2.3.2',",'').replace('trusted financial runner setup failed','trusted TeX runner setup failed')
exec(compile(source,'<trusted-tex-runner>','exec'),globals())
SOURCE_TEMPLATE_SHA256=hashlib.sha256((R/'financial_grader_setup.py').read_bytes()).hexdigest()
