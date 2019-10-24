from rdkit import Chem
from rdkit.Chem.Scaffolds import MurckoScaffold
import json


def read_json_file(filename, choice):
    '''
    reads a json file name in this format
    {"CHEMBL21": ["Nc1ccc(cc1)S(=O)(=O)N", 628.0]} output smiles and activity dictionary based on choice
    smiles_dict = 'CHEMBL189352': 'COc1ccc2c(cnn2n1)c3ccnc(Nc4ccc(cc4)C#N)n3'
    activity_dict = 'CHEMBL359794': 1.0
    :param filename: a json file name
    :param choice: either 'smiles_dict' or 'activity_dict'
    :return: smiles or activity dictionary
    '''
    smiles_dict = {}
    activity_dict = {}
    with open(filename, 'r') as json_data:
        doc = json.load(json_data)
        for row in doc:
            smiles_dict[row] = doc[row][0]
            activity_dict[row] = doc[row][1]
    if choice == 'smiles_dict':
        return smiles_dict
    elif choice == 'activity_dict':
        return activity_dict


def getMurckoScaffold(smiles_dict):
    '''Reads a smile dictionary in this format
    'CHEMBL189352': 'COc1ccc2c(cnn2n1)c3ccnc(Nc4ccc(cc4)C#N)n3'
    Returns a dictionary of Murcko scaffolds with the corresponding molecules
    'Cc1n[nH]c2ccc(cc12)c3cncc(OC[C@@H](N)Cc4ccccc4)c3': 'CHEMBL379218'
    :param smiles_file: smiles dictionary
    :return: dictionary of scaffolds and chembl_id
    '''
    """ """
    smiles_list = smiles_dict.values()
    chembl_id_list = smiles_dict.keys()

    mols_list = [Chem.MolFromSmiles(x) for x in smiles_list]

    scaffolds = {}
    for mol, y in zip(mols_list, chembl_id_list):


        core = MurckoScaffold.GetScaffoldForMol(mol)
        scaffold = Chem.MolToSmiles(core)

        if scaffold in scaffolds:
             scaffolds[scaffold].append(y)
        else:
             scaffolds[scaffold] = []
             scaffolds[scaffold].append(y)

    return scaffolds

def SelectActives(mols, activities):
    '''
    :param mols: name of the molecule or ChEMBL id
    :param activities: dictionary of activity
    :return: Returns the list of molecules for each scaffold sorted based on their activities
    '''
    scaffold_activities = {}
    for mol in mols:
        scaffold_activities[mol] = activities[mol]

    return sorted(scaffold_activities, key=scaffold_activities.get)


def mt100scaffolds(scaffolds, activities, smiles):
    '''
    Returns the most active molecule for each scaffold in this format
    'N#Cc1ccc(Nc2nccc(n2)c3cnn4ncccc34)cc1': 'CHEMBL359794'
    :param scaffolds: dictionary of scaffolds
    :param activities: dictionary of activities
    :param smiles: dictionary of smiles
    :return: a dictionary of actives
    '''
    actives = {}
    for scaffold, mol_names in scaffolds.items():
        best = SelectActives(mol_names, activities)[0]
        actives[smiles[best]] = best
    return actives


def lt100scaffolds(scaffolds, activities, smiles):
    '''The number of highest affinity ligands taken from each Murcko scaffold are increased
    until we achieve at least 100 ligands or until all ligands are included
    'N#Cc1ccc(Nc2nccc(n2)c3cnn4ncccc34)cc1': 'CHEMBL359794'
    :param scaffolds: dictionary of scaffolds
    :param activities: dictionary of activities
    :param smiles: dictionary of smiles
    :return: dictionary of actives
    '''
    """ """
    actives = {}
    k = 0
    while len(actives) <= 100:
        for scaffold, mol_names in scaffolds.items():
            if len(mol_names) > k:
                best = SelectActives(mol_names, activities)[k]
                actives[smiles[best]] = best
        k += 1
        if len(actives) == len(smiles):
            break

    return actives

activity_dict = read_json_file('P24941.json', choice='activity_dict')
smiles_dict = read_json_file('P24941.json', choice='smiles_dict')

dbofscaffolds = getMurckoScaffold(smiles_dict)
print(len(dbofscaffolds))
if len(dbofscaffolds) >= 100:
    actives = mt100scaffolds(dbofscaffolds, activity_dict, smiles_dict)
    #print(actives)
elif len(dbofscaffolds) < 100:
    actives = lt100scaffolds(dbofscaffolds, activity_dict, smiles_dict)
    print(actives)