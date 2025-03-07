####################################
# Pre-lab 7a: Data processing 
# UK Household Longitudinal Survey
# https://www.understandingsociety.ac.uk/documentation/mainstage
# Panel data with three time periods (waves 2, 4, and 6) 
# trade union membership: this question was asked in UKHLS 2, 4, 6, 
#   and 8 only.
####################################

# Check the working directory
import os
print(os.getcwd())

# Change the working directory to your folder with data
os.chdir('\\Users\\rk17311\\OneDrive - University of Bristol\\2023 24\\Teaching\\EconometricsWpython\\Data\\UKHLS')
print(os.getcwd())

# Import the libraries
import numpy as np
import pandas as pd

# Import data. UKHLS comes in Stata format
df1= pd.read_stata('ub_indresp.dta')
df2= pd.read_stata('ud_indresp.dta') 
# there is an error, due to a variable d_yafuta having non-unique labels
# I can use convert_categoricals = False option, but that will affect all 
# variables and data in an undesirable way.
# Instead, I modified the stata file by dropping that variable which is not relevant 
# for us

df2= pd.read_stata('ud_indresp_1.dta') 
df3= pd.read_stata('uf_indresp_1.dta') # same here as above
######################################
# Check the data: 
    # If you are using Spider, Check the data in Variable Explorer.
    # If you are using Google Colab, check the info()
# df1 and df2 has same variables (columns) with df1 'a_' prefix and 
# df2 'b_' prefix

# Stata datasets generally have variable labels (short definitions)
# Lets extract them in a dictionary
df1_forlabel= pd.read_stata('ub_indresp.dta', iterator = True)
labels_df1 = df1_forlabel.variable_labels()
    # If you are using Spider, check the Variable Explorer for the labels
    # If you are using Google Colab, type labels_df1 to see the labels
######################################

# Lets remove the prefixes and add wave to format panel data

df1.columns = df1.columns.str.removeprefix('b_')
df2.columns = df2.columns.str.removeprefix('d_')   
df3.columns = df3.columns.str.removeprefix('f_')   

df1['wave']= 2 # generate the wave variable
df2['wave']= 4 # generate the wave variable
df3['wave']= 6 # generate the wave variable

#######################################
# Combine the two waves
# Method (1) Using merge
# https://pandas.pydata.org/docs/user_guide/merging.html#database-style-dataframe-or-named-series-joining-merging

data1 = df1.merge(df2, how='left', on='pidp')
data1.info()

# Check the data: 
    # If you are using Spider, Check the data in Variable Explorer.
    # If you are using Google Colab, check the info()
##  how many observations are there?
##  how many variables?
##  what did the merge function do here?
##  why do we have _x and _y suffixes in UKHLS?
##  why didn't we get higher observations with i,t indices?

# We need stack them vertically to get to panel format
# For this to work, we have to use the columns that are not duplicate in names
df11 = df1.set_index(['pidp', 'wave'])
df12 = df2.set_index(['pidp', 'wave'])
cols_to_use = df12.columns.difference(df11.columns)
data1 = pd.merge(df11, df12[cols_to_use], left_index=True, right_index=True, how='outer')

# Lets not use merge for the next data, rather do something more efficient.

# Method (2) (Efficient) using concat
# https://pandas.pydata.org/docs/user_guide/merging.html#concatenating-objects
data2 = pd.concat([df1, df2, df3], axis=0)

# Now check data2, and compare the number of observations and variables
#######################################


# Variable selection 
# Let us select key variables for Lab 7 analysis

# employed : jbft_dv : Full or part-time employee
# wage: paygu_dv : usual gross pay per month: current job
# educ: scend : School leaving age
# age: age_dv : Age, derived from dob_dv and intdat_dv
# sex :  sex
# union membership : tuin1 : Member of workplace union
# marital status: mlstat : Present legal marital status
# black : racel_dv: Ethnic group incorp. all waves, codings, modes and bhps

data = data2[[ "pidp","wave", "jbft_dv", "paygu_dv", "scend", "age_dv", "sex", "tuin1", "mlstat", "racel_dv" ]]

# Check variable categories and generate dummy variables

# Full time employee dummy:
data['jbft_dv'].value_counts()

# multiple categories, two of them showing employee status. 

def dummy_ft (x):
    if x =='FT employee': return 1
    elif x == 'PT employee': return 0
    else: return 'nan'
data['ft']= data['jbft_dv'].apply(dummy_ft)
data['ft'].value_counts()

# male dummy
data['sex'].value_counts()
data['male'] = (data['sex']=='male').astype(int)
data['male'].value_counts()

# Union member dummy
data['tuin1'].value_counts()

def dummy_uni (x):
    if x =='yes': return 1
    elif x == 'no': return 0
    else: return 'nan'
    
data['union']= data['tuin1'].apply(dummy_uni)
data['union'].value_counts()


# married dummy
data['mlstat'].value_counts()
data['married'] = (data['mlstat']=='married').astype(int)

# Black dummy
data['racel_dv'].value_counts()


data['black1'] = (data['racel_dv']=='african (black or black britih)'). astype(int)
data['black2'] = (data['racel_dv']=='caribbean (black or black british)'). astype(int) 
data['black3'] = (data['racel_dv']=='any other black background (black or black britih)').astype(int)
data['black'] = data['black1']+ data['black2'] + data['black3']

UKHLS = data[[ "pidp","wave", "ft", "paygu_dv", "scend", "age_dv", "male", "union", "married", "black" ]]

UKHLS = UKHLS.rename(columns = {'paygu_dv': 'wage', 'age_dv': 'age'})

UKHLS.to_csv('UKHLS.csv') 

##############################################
# There are a lot of observations in educ with 'inapplicable'
# This reduces the sample size drastically for regressions
# It is possible that in wave 1 those who replied to this question
# If they are employed, having wages, we can use wave 1 education

df_t= pd.read_stata('ua_indresp.dta')

# need to match with pidp
df_t = df_t.set_index(['pidp'])
UKHLS = UKHLS.set_index(['pidp'])

# Lets replace in a new column to keep track of changes
UKHLS["scend_1"] = UKHLS["scend"]
UKHLS.loc[UKHLS.scend_1 == 'inapplicable', 'scend_1'] = df_t['a_scend']

# Lets compare
UKHLS["scend_1"].value_counts()
UKHLS["scend"].value_counts()

UKHLS.to_csv('UKHLS.csv') 

##############################################




