
import pandas as pd
from pandas import DataFrame
import numpy as np
import random
import statsmodels.discrete.discrete_model as sm
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier as rf



def Init_CPS_Vars(CPS):

    '''
        Variables within the CPS that we use:

    ssi_val     Supplemental Security income amount received
    ssi_yn      Supplemental Security income received
    ssikidyn    Supplemental Security income, child received
    rednssi1    Supplemental Security income, reason 1
    rednssi2    Supplemental Security income, reason 2
    marsupwt    March supplement final weight
    a_age       Age
    a_spouse    Marital Status
    fownu18     Non-married children under 18 in household
    gestfips    FIPS State Code
    pedisdrs    Disability, dressing or bathing
    pedisear    Disability, hearing
    pediseye    Disability, seeing
    pedisout    Disability, doctor visits, shopping alone
    pedisphy    Disability, walking, climbing stairs
    pedisrem    Disability, remembering
    dis_hp      Health problem or a disability which prevents working
    rsnnotw     Reason for not working
    vet_typ1    Veterans payments, type 1
    pemlr       Monthly labor force recode
    mcare       Medicare coverage
    wsal_val    Total wage and salary earnings value
    semp_val    Own business self-employment earnings, total value
    frse_val    Farm self-employment earnings, total value
    ss_val      Social Security payments received, value
    rtm_val     Retirement income received, total amount
    oi_off      Income sources, other
    oi_val      Income, other (amount)
    uc_yn       Unemployment compensation benefits received
    uc_val      Unemployment compensation benefits value
    int_yn      Interest received
    int_val     Interest income received, amount+
    ffpos       Record type and sequence indicator (similar numbers
            indicate in same family)
    fh_seq      Household sequence number (similar number indicate same Household)
    finc_ssi    Supplemental Security benefits (Family)
    ftot_r      Total family income
    ftotval     Total family income
    ptot_r      Person income, total
    ptotval     Person income, total
    peridnum    Unique Person identifier
    '''
    # These lists contain the column names that contain the missing data
    Noneornot = ['ssi_val', 'csp_val', 'rnt_val', 'div_val', 'vet_val', 'wsal_val', 'semp_val', 'frse_val', 'ss_val', 'rtm_val', 'oi_val', 'uc_val', 'int_val', 'ftotval', 'ptotval', 'hwsval', 'pearnval', 'htotval']
    NotInUniv = ['ssi_yn', 'dis_hp', 'rsnnotw', 'vet_typ1', 'uc_yn', 'int_yn', 'ptot_r', 'paw_yn', 'earner', 'hfdval']
    NIU = ['ssikidyn', 'resnssi1', 'resnssi2', 'pedisdrs', 'pedisear', 'pediseye', 'pedisout', 'pedisphy', 'pedisrem', 'pemlr', 'oi_off']
    # Add variables that indicate which entries of which columns contain missing values
    for col in Noneornot:
        CPS[col + '_missing_NoneIn'] = np.where(CPS[col] == 'None or not in universe', 1, 0)
    for col in NotInUniv:
        CPS[col + '_missing_NotIn'] = np.where(CPS[col] == 'Not in universe', 1, 0)
    for col in NIU:
        CPS[col + '_missing_NIU'] = np.where(CPS[col] == 'NIU', 1, 0)
    
    # Setting missing values equal to zero after adding binary variable
    CPS = CPS.replace({'None or not in universe' : 0.}, regex = True)
    CPS = CPS.replace({'Not in universe' : 0.}, regex = True)
    CPS = CPS.replace({'NIU' : 0.}, regex = True)
    CPS = CPS.replace({'Did not receive SSI' : 0.}, regex = True)
    CPS = CPS.replace({'Received SSI' : 1.}, regex = True)
    CPS = CPS.replace({'No' : 0.}, regex = True)
    # Creating unearned income variable
    CPS_unearned = (CPS[['fssval' ,'fretval' ,'foival' , 'fucval' , 'fintval', 'frntval', 'fdivval', 'fvetval', 'fcspval']].astype(float)).copy()
    unearned_income = CPS_unearned.sum(axis = 1)
    # Creating earned income variable
    CPS_earned = (CPS[['fwsval' ,'fseval','ffrval']].astype(float)).copy()
    earned_income = CPS_earned.sum(axis = 1)
    # Determining current recipients of SSI benefit
    CPS['current_recipient'] = np.where((CPS.ssi_yn =='Yes'), 1, 0)
    CPS = CPS.replace({'Yes' : 1.}, regex = True)

    # CPS['fssival'] = (CPS['fssival'].astype(float)).copy()
    CPS['earned_income'] = earned_income
    CPS['unearned_income'] = unearned_income
    # Below is a list of variables that are categorical but represented as strings
    cols = ['a_ftpt', 'filestat', 'peridnum', 'ptot_r','ftot_r', 'pemlr', 'resnssi1', 'resnssi2', 'a_maritl', 'fownu18', 'oi_off', 'rsnnotw', 'pedisdrs', 'earner', 'prdtrace','hea', 'earner']
    for col in cols:#Iterating through all of these categorical strings and converting to numbers below
        CPS[col] = CPS[col].astype('category')

    cat_columns = CPS.select_dtypes(['category']).columns
    CPS[cat_columns] = CPS[cat_columns].apply(lambda x: x.cat.codes)

    return CPS


CPS = pd.read_csv('asec2015_pubuse.csv')
CPS = Init_CPS_Vars(CPS)

CPS.a_age = np.where(CPS.a_age == "80-84 years of age",
                     np.mean(np.arange(80,85)),
                     CPS.a_age)
CPS.a_age = np.where(CPS.a_age == "85+ years of age",
                     np.mean(np.arange(85,96)),
                     CPS.a_age)
CPS.a_age = pd.to_numeric(CPS.a_age)
CPS['80_84__missing'] = np.where(CPS['a_age'] == np.mean(np.arange(80,85)), 1, 0)
CPS['85_95__missing'] = np.where(CPS['a_age'] == np.mean(np.arange(85,86)), 1, 0)

key1 = CPS.columns.to_series().groupby(CPS.dtypes).groups.keys()[1]
cols =  CPS.columns.to_series().groupby(CPS.dtypes).groups[key1].values
for col in cols:
    CPS[col] = CPS[col].astype('category')
CPS[cols] = CPS[cols].apply(lambda x: x.cat.codes)
CPS = CPS.fillna(0) 

CPS_unearned = (CPS[['fssval' ,'fretval' ,'foival' , 'fucval' , 'fintval', 'frntval', 'fdivval', 'fvetval', 'fcspval']].astype(float)).copy()
unearned_income = CPS_unearned.sum(axis = 1)
# Creating earned income variable
CPS_earned = (CPS[['fwsval' ,'fseval','ffrval']].astype(float)).copy()
earned_income = CPS_earned.sum(axis = 1)

CPS['fam_earned_income'] = earned_income
CPS['fam_unearned_income'] = unearned_income
# CPS.to_pickle('CPS_family.pickle')
# CPS_dataset = pd.read_pickle('CPS_family.pickle')
CPS_dataset = CPS.copy()


#Earned income
p_earned = CPS_dataset.wsal_val + CPS_dataset.semp_val + CPS_dataset.frse_val #individual earned income
CPS_dataset['p_earned'] = p_earned


#Net Income
CPS_dataset['family_net_income'] = p_earned


#disabled (check reg if categorical or binary is better after the sum)
CPS_dataset['disability'] = np.zeros(len(CPS_dataset))
CPS_dataset.disability = np.where(CPS_dataset.pedisdrs == 1, 1, CPS_dataset.disability)
CPS_dataset.disability = np.where(CPS_dataset.pedisear == 1, 1, CPS_dataset.disability)
CPS_dataset.disability = np.where(CPS_dataset.pediseye == 1, 1, CPS_dataset.disability)
CPS_dataset.disability = np.where(CPS_dataset.pedisout == 1, 1, CPS_dataset.disability)
CPS_dataset.disability = np.where(CPS_dataset.pedisphy == 1, 1, CPS_dataset.disability)
CPS_dataset.disability = np.where(CPS_dataset.pedisrem == 1, 1, CPS_dataset.disability)


Rf = rf(n_estimators = 200, min_samples_leaf = 6, max_depth = 5) # Creating Random Forest 
CPS_use = CPS_dataset.drop('peridnum', 1)

#Splitting data into training and test sets
train = CPS_use.sample(frac=0.8, random_state=1)
train_x = train.copy()
train_x = train_x.drop(['pothval', 'hothval', 'fothval','strkuc','subuc','fam_unearned_income','unearned_income','finc_uc', 'hinc_uc', 'hucval', 'fucval', 'i_ucval','hunits', 'hhpos', 'h_seq', 'hrecord', 'ph_seq','uc_val_missing_NoneIn',                        
    'uc_val','uc_yn', 'hunits', 'hhpos','h_seq', 'hsup_wgt', 'fsup_wgt', 'marsupwt','h_idnum1'],1)



test_x = CPS_use.loc[~CPS_use.index.isin(train_x.index)]
test_y = test_x['uc_yn']
test_x = test_x.drop(['pothval', 'hothval', 'fothval','strkuc','subuc','fam_unearned_income','unearned_income','finc_uc', 'hinc_uc', 'hucval', 'fucval', 'i_ucval','hunits', 'hhpos', 'h_seq', 'hrecord', 'ph_seq', 'uc_val_missing_NoneIn',                      
    'uc_val','uc_yn', 'hunits', 'hhpos','h_seq', 'hsup_wgt', 'fsup_wgt', 'marsupwt','h_idnum1'],1)


# Fitting the Random Forest model to the training set
Rf.fit(train_x, train['uc_yn'])
print Rf.feature_importances_, train_x.columns.values
predictions = Rf.predict(test_x)
print 'score:', Rf.score(test_x, test_y) # Printing Random Forest accuracy
fimp = Rf.feature_importances_
colvals = train_x.columns.values



features = Rf.feature_importances_
maxes = np.argsort(features)[::-1]
print maxes
print list(train_x[maxes].columns.values)
print features[maxes]


# important features: 

# 'lkstrch', 'lkweeks', 'wexp', 'weuemp', 'wkcheck', 
# 'wkswork', 'a_wkstat', 'a_lfsr', 'pemlr', 'prswkxpns', 
# 'a_wkslk', 'pruntype', 'a_explf', 'prwkstat', 'a_wksch', 
# 'hrswk', 'a_untype', 'wewkrs', 'pehruslt', 'age1',
#  'filestat', 'wemind', 'hrcheck', 'a_whenlj', 'weclw', 
#  'phmemprs', 'weind', 'ptyn', 'ern_srce', 'tax_inc', 'occup',
#   'hiemp', 'ptot_r', 'wsal_yn', 'clwk', 'ptotval', 'fedtax_ac', 
#   'industry', 'fedtax_bc', 'fica', 'peioind', 'a_age', 'pyrsn', 'peioocc'

get_probs = CPS_use.copy()
get_probs = get_probs.drop(['pothval', 'hothval', 'fothval','strkuc','subuc','fam_unearned_income','unearned_income','finc_uc', 'hinc_uc', 'hucval', 'fucval', 'i_ucval','hunits', 'hhpos', 'h_seq', 'hrecord', 'ph_seq', 'uc_val_missing_NoneIn',                      
    'uc_val','uc_yn', 'hunits', 'hhpos','h_seq', 'hsup_wgt', 'fsup_wgt', 'marsupwt','h_idnum1'],1)


prediction_vec = Rf.predict_proba(get_probs)
print prediction_vec
    
np.savetxt('rf_probs.csv', prediction_vec)