# Learning Progress
## Knowledges check
### Module 2
- Traditional Data Teams
    - Data engineers are responsible for maintaining data infrastructure and the ETL process for creating tables and views.
    - Data analysts focus on querying tables and views to drive business insights for stakeholders.
- ETL and ELT
    - ETL (extract transform load) is the process of creating new database objects by extracting data from multiple data sources, transforming it on a local or third party machine, and loading the transformed data into a data warehouse.
    - ELT (extract load transform) is a more recent process of creating new database objects by first extracting and loading raw data into a data warehouse and then transforming that data directly in the warehouse.
    - The new ELT process is made possible by the introduction of cloud-based data warehouse technologies.
- Analytics Engineering
    - Analytics engineers focus on the transformation of raw data into transformed data that is ready for analysis. This new role on the data team changes the responsibilities of data engineers and data analysts.
    - Data engineers can focus on larger data architecture and the EL in ELT.
    - Data analysts can focus on insight and dashboard work using the transformed data.
    - Note: At a small company, a data team of one may own all three of these roles and responsibilities. As your team grows, the lines between these roles will remain blurry.
- dbt
    - dbt empowers data teams to leverage software engineering principles for transforming data.
    - The focus of this course is to build your analytics engineering mindset and dbt skills to give you more leverage in your work.

#### Recap
![alt text](../images/image_00.png)
![alt text](../images/image_01.png)
![alt text](../images/image_02.png)
![alt text](../images/image_03.png)

### Module 3 (Set Up dbt Cloud)

#### Create the dbt trial and snowflake trial account
For the snowflake trial account, choose the Enterprise Snowflake edition so you have ACCOUNTADMIN access
![alt text](../images/image_05.png)
![alt text](../images/image_04.png)

#### Create a new Snowflake worksheet
- Log in to your trial Snowflake account.
- In the Snowflake UI, click + Create in the left-hand corner, underneath the Snowflake logo, which opens a dropdown. Select the first option, SQL Worksheet.
![alt text](../images/image_06.png)

#### Load data to SnowFlake
The data used here is stored as CSV files in a public S3 bucket and the following steps will guide you through how to prepare your Snowflake account for that data and upload it.
1. Create a new virtual warehouse, two new databases (one for raw data, the other for future dbt development), and two new schemas (one for jaffle_shop data, the other for stripe data).
To do this, run these SQL commands by typing them into the Editor of your new Snowflake worksheet and clicking Run in the upper right corner of the UI:
```sql
create warehouse transforming;
create database raw;
create database analytics;
create schema raw.jaffle_shop;
create schema raw.stripe;
```
![alt text](../images/image_07.png)

2. In the raw database and jaffle_shop and stripe schemas, create three tables and load relevant data into them:
- First, delete all contents (empty) in the Editor of the Snowflake worksheet. Then, run this SQL command to create the customer table:
```sql
create table raw.jaffle_shop.customers 
( id integer,
  first_name varchar,
  last_name varchar
);
```

- Delete all contents in the Editor, then run this command to load data into the customer table:
```sql
copy into raw.jaffle_shop.customers (id, first_name, last_name)
from 's3://dbt-tutorial-public/jaffle_shop_customers.csv'
file_format = (
    type = 'CSV'
    field_delimiter = ','
    skip_header = 1
    ); 
```

![alt text](../images/image_08.png)

- Delete all contents in the Editor (empty), then run this command to create the orders table:
```sql
create table raw.jaffle_shop.orders
( id integer,
  user_id integer,
  order_date date,
  status varchar,
  _etl_loaded_at timestamp default current_timestamp
); 
```
- Delete all contents in the Editor, then run this command to load data into the orders table:
```sql
copy into raw.jaffle_shop.orders (id, user_id, order_date, status)
from 's3://dbt-tutorial-public/jaffle_shop_orders.csv'
file_format = (
    type = 'CSV'
    field_delimiter = ','
    skip_header = 1
    );
```

![alt text](../images/image_09.png)

- Delete all contents in the Editor (empty), then run this command to create the payment table:
```sql
create table raw.stripe.payment 
( id integer,
  orderid integer,
  paymentmethod varchar,
  status varchar,
  amount integer,
  created date,
  _batched_at timestamp default current_timestamp
);
```

- Delete all contents in the Editor, then run this command to load data into the payment table:
```sql
copy into raw.stripe.payment (id, orderid, paymentmethod, status, amount, created)
from 's3://dbt-tutorial-public/stripe_payments.csv'
file_format = (
    type = 'CSV'
    field_delimiter = ','
    skip_header = 1
    );
```
![alt text](../images/image_10.png)


3. Verify that the data is loaded by running these SQL queries. Confirm that you can see output for each one.
```sql
select * from raw.jaffle_shop.customers;
select * from raw.jaffle_shop.orders;
select * from raw.stripe.payment;  
```

#### Connect dbt to Snowflake
Follow this guideline: [https://docs.getdbt.com/guides/snowflake?step=4#connect-dbt-to-snowflake](https://docs.getdbt.com/guides/snowflake?step=4#connect-dbt-to-snowflake)

There are two ways to connect dbt to Snowflake. The first option is Partner Connect, which provides a streamlined setup to create your dbt account from within your new Snowflake trial account. The second option is to create your dbt account separately and build the Snowflake connection yourself (connect manually). If you want to get started quickly, dbt Labs recommends using Partner Connect. If you want to customize your setup from the very beginning and gain familiarity with the dbt setup flow, dbt Labs recommends connecting manually.

Here, i will use the manual connection to connect dbt to the Snowflake
1. Create a new project in dbt. Navigate to Account settings (by clicking on your account name in the left side menu), and click + New Project. Enter a project name and click Continue.** *(has been created yet)***

2. For the warehouse, click Snowflake then Next to set up your connection.

3. Enter your Settings for Snowflake with:

- Account — Find your account by using the Snowflake trial account URL and removing snowflakecomputing.com. The order of your account information will vary by Snowflake version. For example, Snowflake's Classic console URL might look like: oq65696.west-us-2.azure.snowflakecomputing.com. The AppUI or Snowsight URL might look more like: snowflakecomputing.com/west-us-2.azure/oq65696. In both examples, your account will be: oq65696.west-us-2.azure. For more information, see Account Identifiers in the Snowflake docs.

  ✅ db5261993 or db5261993.east-us-2.azure

  ❌ db5261993.eu-central-1.snowflakecomputing.com

![alt text](../images/image_11.png)

- Role — Leave blank for now. You can update this to a default Snowflake role later.

- Database — analytics. This tells dbt to create new models in the analytics database.

- Warehouse — transforming. This tells dbt to use the transforming warehouse that was created earlier.

![alt text](../images/image_12.png)

4. Enter your Development Credentials for Snowflake with:

- Username — The username you created for Snowflake. The username is not your email address and is usually your first and last name together in one word.
- Password — The password you set when creating your Snowflake account.
- Schema — You’ll notice that the schema name has been auto created for you. By convention, this is dbt_<first-initial><last-name>. This is the schema connected directly to your development environment, and it's where your models will be built when running dbt within the Studio IDE.
- Target name — Leave as the default.
- Threads — Leave as 4. This is the number of simultaneous connects that dbt will make to build models concurrently.

5. Click Test Connection. This verifies that dbt can access your Snowflake account.
![alt text](../images/image_13.png)

#### Set up a dbt managed repository
Follow this guideline here: [https://docs.getdbt.com/guides/snowflake?step=5#set-up-a-dbt-managed-repository](https://docs.getdbt.com/guides/snowflake?step=5#set-up-a-dbt-managed-repository)


If using the Partner Connect, can skip to initializing the dbt project as the Partner Connect provides u with a managed repository. Otherwise, you will need to create your repository connection.

When you develop in dbt, you can leverage Git to version control your code.

To connect to a repository, you can either set up a dbt-hosted managed repository or directly connect to a supported git provider. Managed repositories are a great way to trial dbt without needing to create a new repository. In the long run, it's better to connect to a supported git provider to use features like automation and continuous integration.

To set up a managed repository:

- Under "Setup a repository", select Managed.
- Type a name for your repo such as bbaggins-dbt-quickstart
- Click Create. It will take a few seconds for your repository to be created and imported.
- Once you see the "Successfully imported repository," click Continue.

#### Initialize your dbt project​ and start developing
Follow this guideline: [https://docs.getdbt.com/guides/snowflake?step=6#initialize-your-dbt-project-and-start-developing](https://docs.getdbt.com/guides/snowflake?step=6#initialize-your-dbt-project-and-start-developing)

Now that you have a repository configured, you can initialize your project and start development in dbt:

- Click Start developing in the Studio IDE. It might take a few minutes for your project to spin up for the first time as it establishes your git connection, clones your repo, and tests the connection to the warehouse.
- Above the file tree to the left, click Initialize your project. This builds out your folder structure with example models.
- Make your initial commit by clicking Commit and sync. Use the commit message initial commit. This creates the first commit to your managed repo and allows you to open a branch where you can add new dbt code.
- You can now directly query data from your warehouse and execute dbt run. You can try this out now:
    - Click + Create new file, add this query to the new file, and click Save as to save the new file
    ```sql
    select * from raw.jaffle_shop.customers
    ```
    - In the command line bar at the bottom, enter dbt run and click Enter. You should see a dbt run succeeded message.

    ![alt text](../images/image_14.png)
