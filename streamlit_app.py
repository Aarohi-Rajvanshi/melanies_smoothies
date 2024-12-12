# Import python packages
import streamlit as st
import requests
from snowflake.snowpark.functions import col, when_matched

# Write directly to the app
st.title(":cup_with_straw: Customize your Smoothie! :cup_with_straw:")
st.write("""Orders that need to filled.""")

cnx = st.connection("snowflake")
session = cnx.session()

name_on_order = st.text_input('Name on Smoothie:')

my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'),col('SEARCH_ON'))
st.write('The name on your Smoothie will be:', name_on_order)
#cnx = st.connection("snowflake")
#session = cnx.session()

#my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'),col('SEARCH_ON'))
#st.dataframe(data=my_dataframe, use_container_width = True)
#st.stop()
pd_df=my_dataframe.to_pandas()


ingredients_list = st.multiselect(
    'Choose upto 5 ingredients:'
    ,my_dataframe
    ,max_selections = 5
)
if ingredients_list:
    ingredients_string = ''
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        
        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit_chosen,' is ', search_on, '.')
        
        st.subheader(fruit_chosen + 'Nutrition Information')
        fruityvice_response = requests.get("https://my.fruityvice.com/api/fruit/watermelon"+search_on)
        fv_df = st.dataframe(data=fruityvice_response.json(), use_container_width=True)
    

    my_insert_stmt = """insert into smoothies.public.orders(ingredients)
        values ('""" + ingredients_string + """')"""
    time_to_insert = st.button('Submit Order')
    #pd_df=my_dataframe.to_pandas()
    st.dataframe(pd_df)
    st.stop()

if my_dataframe:
    editable_df = st.data_editor(my_dataframe)
    submitted = st.button('Submit')
    if submitted:
        og_dataset = session.table("smoothies.public.orders")
        edited_dataset = session.create_dataframe(editable_df)
        try:
            og_dataset.merge(edited_dataset
                         , (og_dataset['ORDER_UID'] == edited_dataset['ORDER_UID'])
                         , [when_matched().update({'ORDER_FILLED': edited_dataset['ORDER_FILLED']})]
    
                        )
            st.success('Order(s) Updated!', icon="✅")
        except:
            st.write('Something went wrong.')
else:
    st.success('There are no pending orders right now',icon="✅")







