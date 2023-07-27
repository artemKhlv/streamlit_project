import streamlit as st
from rdkit import Chem
from stmol import showmol
import py3Dmol
from rdkit.Chem import AllChem
import deepchem as dc
import pandas as pd
from urllib.request import urlopen
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from st_pages import Page, show_pages
show_pages(
    [
        # Page("main.py", "Home", "🏠"),
        Page("molecule_examine.py", "Molecule Examine", "🧫"),
        Page("chat.py", "ChatAI", "🪬"),
        Page("about_us.py", "About us", "🧑🏻‍🔬")
    ]
)


def CIRconvert(smi):
    url = "https://cactus.nci.nih.gov/chemical/structure/" + smi + "/formula"
    ans = urlopen(url).read().decode('utf8')
    ans1 = "Формула вещества: " + ans
    return ans1


def getSolubility(a):
    c = a[0][0]
    print(c)
    b = "Расстворимость вещества: " + c.astype(str)
    return b


def getPearson_r2_train_score(a):
    b = "Коэффициент корреляции для тренировочного набора: " + a.astype(str)
    return b


def getPearson_r2_test_score(a):
    b = "Коэффициент корреляции для проверочного набора: " + a.astype(str)
    return b


def makeblock(smi):
    mol = Chem.MolFromSmiles(smi)
    mol = Chem.AddHs(mol)
    AllChem.EmbedMolecule(mol)
    mblock = Chem.MolToMolBlock(mol)
    return mblock


def render_mol(xyz):
    xyzview = py3Dmol.view()
    xyzview.addModel(xyz, 'mol')
    xyzview.setStyle({'stick': {}})
    xyzview.setBackgroundColor('white')
    xyzview.zoomTo()
    showmol(xyzview, height=500, width=2000)


st.title('3D модель вещества и прогноз растворимости 🧬')
st.write('Перед тем, как начать нужно отметить, для чего нужна информация о растворимости вещества (молекулы). '
         '**Расстворимость** - это мера того, насколько легко вещество растворяется в воде. '
         'Это свойство жизненно важно для любого химического вещества, которое в дальнейшем будет использоваться в качестве лекарства. '
         'Если оно растворяется с трудом, '
         'то может не попасть в кровоток пациента для оказания терапевтического эффекта. '
         'Химики-фармацевты проводят много времени, модифицируя молекулы для увеличения растворимости препаратов.')
st.write('Чтобы справится с этой задачей, нужно вооружится знанием о том, как правильно представить молекулу или вещество в таком виде, '
         'чтобы программа смогла ее прочитать, построить 3D модель и спрогнозировать расстворимость. '
         'К счастью, решение есть, и оно называется **SMILES** (Simplified Molecular Input Line Entry System или '
         'система упрощённого представления молекул в строке ввода) - это система правил (спецификация) однозначного описания состава и '
         'структуры молекулы химического вещества с использованием строки символов ASCII. '
         'Дабы облегчить ваше восприятие и в полной мере оценить задуманное, в качестве примеров, я приведу для Вас несколько вещест в системе SMILES.')
st.write('1. **Тиамин или витамин B1:** *CC1=C(SC=[N+]1CC2=CN=C(N=C2N)C)CCO* - является незаменимым микроэлементом для людей и животных. Он содержится в пищевых продуктах и коммерчески синтезируется в качестве пищевой добавки или лекарства. Фосфорилированные формы тиамина необходимы для некоторых метаболических реакций, включая расщепление глюкозы и аминокислот.')
st.write('2. **Гормон прогестерон:** *CC(=O)C1CCC2C1(CCC3C2CCC4=CC(=O)CCC34C)C* - эндогенный стероид и прогестагенный половой гормон, оказывающий влияние на менструальный цикл, беременность и эмбриональное развитие у человека и других видов. Он также является ключевым метаболическим промежуточным звеном в производстве других эндогенных стероидов, включая половые гормоны и кортикостероиды, и играет важную роль в функционировании мозга в качестве нейростероида.')
st.write('3. **Кофеин:** *CN1C=NC2=C1C(=O)N(C(=O)N2C)C* - является психоактивным веществом, содержится в кофе, чае, мате, входит в состав энергетиков и многих прохладительных напитков. Также входит в состав аптечных препаратов. Он синтезируется растениями для защиты от насекомых, поедающих листья, стебли и зёрна, а также для поощрения опылителей. У животных и человека кофеин стимулирует центральную нервную систему, усиливает сердечную деятельность, ускоряет пульс, вызывает расширение кровеносных сосудов (преимущественно сосудов скелетных мышц, головного мозга (сужает просвет мозговых артерий), сердца, почек), усиливает мочеотделение и так далее.')
st.write('4. **Левоцитиризин:** *C1CN(CCN1CCOCC(=O)O)C(C2=CC=CC=C2)C3=CC=C(C=C3)Cl*  - антигистаминный препарат, относится к блокаторам Н1-рецепторов гистамина второго поколения, то есть препарат против аллергии.')
st.write('5. **Мехлоретамин:** *CN(CCCl)CCCl* - исторически первый цитостатический препарат (противоопухолевый препарат) алкилирующего типа, производное бис-β-хлорэтиламина, азотистый аналог иприта. Препарат бывает эффективен при остром и хроническом миело- и лимфолейкозе, лимфо- и ретикулосаркоме, лимфогранулематозе, грибовидном микозе, отчасти при мелкоклеточном раке лёгкого.')
smiles = st.text_input('Введите структуру вещества или молекулы по правилу SMILES. '
                       'Например, как показона ниже, это химическое соединение "Тербутрин", который используется для '
                       '"Гербицида" -  вещества, применимый для уничтожения растений.',
                       'CSc1nc(NC(C)C)nc(NC(C)C)n1')

st.success(CIRconvert(smiles),  icon="✅️")
st.write('**Объеснение цветов в 3D модели молекулы** ⬇️')
st.write('Красный - кислород')
st.write('Белый - водород')
st.write('Серый - углерод')
st.write('Голубой - азот')
st.write('Жёлтый - сера или хлор')
st.info('3D модель ниже можно поворачивать',  icon="ℹ️")
blk = makeblock(smiles)
render_mol(blk)
st.write('**Подождите буквально пару секунд, чтобы получить прогноз** ✨')

# ML
solubility_tasks, solubility_datasets, transformers = dc. molnet.load_delaney(featurizer='GraphConv')
train_dataset, valid_dataset, test_dataset = solubility_datasets
model = dc.models.GraphConvModel(n_tasks=1, mode='regression', dropout=0.2)
model.fit(train_dataset, nb_epoch=50)

featurizer = dc.feat.ConvMolFeaturizer()
x = featurizer.featurize(smiles)
predicted_solubility = model.predict_on_batch(x)
st.success(getSolubility(predicted_solubility), icon="✅")
st.write('Пусть дельта (δ) - это наше спрогнозированное значение, тогда если: ')
st.latex(r'''\lim\limits_{\delta\to -3} \delta = Нерастворимо''')
st.latex(r'''\lim\limits_{\delta\to 3} \delta = Растворимо''')
st.latex(r'''\delta \in (-2; 2) = Малорастворимо''')

st.write('')

st.header('Оценка модели')
st.write('В данной задаче использовалась регрессионная графовая сверточная модель, подразумевающая, что метки являются непрерывнами числами и модель '
         'должна стараться возпроизвести их как можно точнее. Этим она отличается от классифицирующей модели, которая пытается предсказать принадлежность '
         'каждой выборки к определенному элементу из набора классов. В качество метрки оценки использовался **коэффициент корреляции Пирсона**')
metric = dc.metrics.Metric(dc.metrics.pearson_r2_score)
train_score = model.evaluate(train_dataset, [metric], transformers)
test_score = model.evaluate(test_dataset, [metric], transformers)
st.write(getPearson_r2_train_score(train_score['pearson_r2_score']))
st.write(getPearson_r2_test_score(test_score['pearson_r2_score']))
