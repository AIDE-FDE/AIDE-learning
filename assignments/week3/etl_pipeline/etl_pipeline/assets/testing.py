from dagster import asset

@asset (
    name="testing_asset"
)
def testing_asset (context):
    context.log.info ("this is the dklaskjdlkasklkdja asset")
    return 1