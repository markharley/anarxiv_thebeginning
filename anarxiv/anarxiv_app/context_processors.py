from collections import OrderedDict


subAnarxivDictionary = OrderedDict({'physics:astro-ph':'Astrophysics', 'physics:cond-mat': 'Condensed Matter', 'physics:gr-qc': 'General Relativity and Quantum Cosmology', 
'physics:hep-ex':'High Energy Physics - Experiment','physics:hep-lat':'High Energy Physics - Lattice', 'physics:hep-ph':'High Energy Physics - Phenomenology',
'physics:hep-th':'High Energy Physics-Theory',
'physics:math-ph': 'Mathematical Physics', 'physics:nlin':'Nonlinear Sciences', 
'physics:nucl-ex':'Nuclear Experiment','physics:nucl-th':'Nuclear Theory','physics:physics':'Physics','physics:quant-ph':'Quantum Physics',
'math':'Maths', 'cs':'Computer Science', 'stat':'Statistics', 'q-bio':'Quantative Biology', 'q-fin':'Quantative Finance'})



def subarxiv_regions(request):
    from django.conf import settings
    return {'subAnarxivs': subAnarxivDictionary}