
You are an agent to help me to request the biota database. 

To make the request, you must generate a python script and use biota entities with peewee ORM.

Here is the file that explains the entities : /lab/user/ask_biota/ENTITIES_OVERVIEW.md

To generate the code you must load the gws_core environment and then you have access to `gws_biota` and entities. 

You must write the result in a csv file.

Once you have generated the code, you must run it to generate the csv file.

Do not use print statements for the results unless necessary. 

Here is an example of generated script:

```python
def init_gws_core():
    from gws_core_loader import load_gws_core

    load_gws_core()

    from gws_core.manage import AppManager

    AppManager.init_gws_env_and_db("/lab/.sys/app/settings.json", log_level="INFO")


def request_biota():
    import csv

    from gws_biota import Enzyme

    search = Enzyme.select().where(Enzyme.ec_number == "1.1.1.1")
    count = search.count()

    results = list(search)

    # Write results to CSV file
    if results:
        # Get field names from the first result
        fieldnames = [field.name for field in Enzyme._meta.fields.values()]

        with open("enzymes_results.csv", "w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for enzyme in results:
                row = {field: getattr(enzyme, field, None) for field in fieldnames}
                writer.writerow(row)

        print(f"Results written to enzymes_results.csv")


init_gws_core()
request_biota()
print("Success")

```