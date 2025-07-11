from minio import Minio
import pandas as pd
from pathlib import Path

# config
# minio
client = Minio (
    "localhost:9000",
    access_key="minio",
    secret_key="minio123",
    secure=False
)

# bucket list
bucket_name = 'warehouse-script'
bucket_list = ['bronze', 'silver', 'gold', 'warehouse-script']

# type of file
objectType = {
    'structure': 'structure',
    'semi-structure': 'semi-structure',
    'unstructure': 'unstructure'
}

# file extension
structureFile = ('.csv')
semi_structureFile = ('.json')
unstructureFile = ('.png', '.jpg', '.parquet', '.pdf')

for bucket in bucket_list:
    if client.bucket_exists (bucket):
        print (" {} is exists".format (bucket))
    else:
        print ("create {} bucket".format (bucket))
        client.make_bucket (bucket)


# upload file
def uploadFile (dataFoler: str, bucket: str, minioClient=client):
    folder = Path(dataFoler)
    all_files = [f for f in folder.iterdir() if f.is_file()]

    file_paths = [str(f.resolve()) for f in all_files]
    file_names = [p.name for p in all_files if p.is_file()]

    for file_path, file_name in zip(file_paths, file_names):
        if file_name.endswith (structureFile):
            minioClient.fput_object (bucket, '{}/{}'.format (objectType['structure'], file_name), file_path)
        elif file_name.endswith (semi_structureFile):
            minioClient.fput_object (bucket, '{}/{}'.format (objectType['semi-structure'], file_name), file_path)
        elif file_name.endswith (unstructureFile):
            minioClient.fput_object (bucket, '{}/{}'.format (objectType['unstructure'], file_name), file_path)
        else:
            print ('Invalid file extentsion')
        
        print ('🍀 upload {} successfully'.format (file_name))


# read file
# read the file and print the first 5 row + save the downloaded file in the temp folder
def read_data (filename, enable_print = True, file_type = ""):
    local_path = './temp/{}'.format (filename)

    match file_type:
        case 'json':
            client.fget_object (bucket_name, 
                                '{}/{}'.format (objectType['semi-structure'], filename), 
                                local_path)
            df = pd.read_json (local_path)
    
        case 'csv':
            client.fget_object (bucket_name, 
                                '{}/{}'.format (objectType['structure'], filename), 
                                local_path)
            df = pd.read_csv (local_path)
    
        case 'parquet':
            client.fget_object (bucket_name, 
                                '{}/{}'.format (objectType['unstructure'], filename), 
                                local_path)
            df = pd.read_parquet (local_path)
        case _:
            print ("🍀 Invalid file type")
            return None
    
    
    if enable_print:
        print (df.head (5))
        print(f"🍀 Total records: {len(df)}")

    return {
        'path': local_path,
        'data': df
    }

# the the new data in the dict format then save them in the temp folder and update them in MinIO 
def write_data (new_data, file_name, file_type, upload = True):
    local_path = './temp/{}'.format (file_name)

    # curr data
    try:
        df = read_data(file_name, enable_print=False, file_type=file_type)['data']
    except:
        df = pd.DataFrame()

    new_df = pd.DataFrame (new_data)
    final_data = pd.concat([df, new_df], ignore_index=True)

    print ('🍀 Append new data successfully')
    print('🍀 New data:')
    print(new_df.head(5))

    match file_type:
        case 'json':
            final_data.to_json (local_path, orient='records', force_ascii=False, indent=4)
        case 'csv':
            final_data.to_csv (local_path, index=False, encoding='utf-8')
        case 'parquet':
            final_data.to_parquet (local_path, index=False)
        case _:
            print ("🍀 Invalid file type")
            return None
        

    if upload:
        uploadFile ('./temp', bucket_name)



if __name__ == "__main__":
    uploadFile ('./data', bucket_name, client)

    mockdata =   [{
        "slug": "womens123",
        "name": "Womens dkjaksldjals",
        "url": "https://dummyjson.com/products/category/womens-watches"
    }]
    write_data (mockdata, 'demo-json.json', 'json')


    new_mock_data = [
        {
            "Index": 17,
            "Name": "Eco Iron Monitor Air",
            "Description": "Color single indeed yard event popular food boy.",
            "Brand": "Barker-Murphy",
            "Category": "Automotive",
            "Price": 982,
            "Currency": "USD",
            "Stock": 47,
            "EAN": "7887280730963",
            "Color": "OliveDrab",
            "Size": "XL",
            "Availability": "out_of_stock",
            "Internal ID": 79
        }
    ]
    write_data (new_mock_data, 'demo-csv.csv', 'csv')


    iris_mock_data = [
        {"sepal.length": 5.1, "sepal.width": 3.5, "petal.length": 1.4, "petal.width": 0.2, "variety": "Setosa"},
        {"sepal.length": 4.9, "sepal.width": 3.0, "petal.length": 1.4, "petal.width": 0.2, "variety": "Setosa"},
        {"sepal.length": 4.7, "sepal.width": 3.2, "petal.length": 1.3, "petal.width": 0.2, "variety": "Setosa"},
        {"sepal.length": 4.6, "sepal.width": 3.1, "petal.length": 1.5, "petal.width": 0.2, "variety": "Setosa"},
        {"sepal.length": 5.0, "sepal.width": 3.6, "petal.length": 1.4, "petal.width": 0.2, "variety": "Setosa"},
        {"sepal.length": 5.4, "sepal.width": 3.9, "petal.length": 1.7, "petal.width": 0.4, "variety": "Setosa"},
        {"sepal.length": 4.6, "sepal.width": 3.4, "petal.length": 1.4, "petal.width": 0.3, "variety": "Setosa"},
        {"sepal.length": 5.0, "sepal.width": 3.4, "petal.length": 1.5, "petal.width": 0.2, "variety": "Setosa"},
        {"sepal.length": 4.4, "sepal.width": 2.9, "petal.length": 1.4, "petal.width": 0.2, "variety": "Setosa"},
        {"sepal.length": 4.9, "sepal.width": 3.1, "petal.length": 1.5, "petal.width": 0.1, "variety": "Setosa"}
    ]
    write_data (iris_mock_data, 'demo-parquet.parquet', 'parquet')


    read_data ('demo-json.json', file_type='json')
    read_data ('demo-parquet.parquet', file_type='parquet')
    read_data ('demo-csv.csv', file_type='csv')

