import streamlit as st
import pandas as pd

import json

from langchain.chat_models import ChatOpenAI
from langchain.agents import create_pandas_dataframe_agent
from langchain.agents.agent_types import AgentType

from streamlit_airtable import AirtableConnection
from chat_open_ai_wrapper import ChatOpenAIWrapper

# Initiate connection to Airtable using st.experimental_connection
airtable_conn = st.experimental_connection("bryan_connection", type=AirtableConnection)
openai_api_key = st.secrets["openai_api_key"]

# Retrieve list of bases, and create a dict of base id to name
bases_list = airtable_conn.list_bases()

bases_id_to_name = {base["id"]: base["name"] for base in bases_list["bases"]}

# Main content pane
with st.container():
    st.markdown("# Airtable Base Explorer")

    selected_base_id = st.selectbox(
        "Select a base to explore:",
        options=list(bases_id_to_name.keys()),
        format_func=lambda base_id: bases_id_to_name[base_id],
        help="If you don't see a base in the list, make sure your personal access token has access to it.",
    )
    base_schema = airtable_conn.get_base_schema(base_id=selected_base_id)

    

    st.markdown("### Table schemas")

    table_schema_tabs = st.tabs([f"{table['name']}" for table in base_schema["tables"]])

    # Show the full schema for each table in an expander
    for i, table_schema in enumerate(base_schema["tables"]):
        this_tab = table_schema_tabs[i]
        this_tab.write(
            f"**{len(table_schema['fields'])} fields** belonging to table `{table_schema['id']}`:"
        )
        fields_df = pd.DataFrame(
            [
                {
                    "name": item["name"],
                    "id": item["id"],
                    "type": item["type"],
                    "choices": [
                        choice["name"] for choice in item["options"].get("choices", [])
                    ]
                    if item["type"] in ["singleSelect", "multipleSelects"]
                    else None,
                    "linked_table_id": item["options"]["linkedTableId"]
                    if item["type"] in ["multipleRecordLinks"]
                    else None,
                    "deep_link": f"https://airtable.com/{selected_base_id}/{table_schema['id']}/{item['id']}",
                }
                for item in table_schema["fields"]
            ]
        )
        this_tab.dataframe(
            fields_df,
            column_config={"deep_link": st.column_config.LinkColumn()},
            hide_index=True,
        )

        col1, col2 = this_tab.columns(2)

        col1.download_button(
            "Download list of fields as CSV",
            fields_df.to_csv(index=False).encode("utf-8"),
            f"table-schema-{selected_base_id}-{table_schema['id']}.csv",
            "text/csv",
        )

        col2.download_button(
            "Download full table schema as JSON",
            json.dumps(table_schema),
            f"table-schema-{selected_base_id}-{table_schema['id']}.json",
            "application/json",
        )

    st.divider()
    st.markdown("### AI")

    if not openai_api_key.startswith("sk-"):
        st.warning(
            "Please enter your OpenAI API in the configuration question to the left to test the AI functionality",
            icon="⚠",
        )
    else:
        # Select a table to query
        table_for_ai = st.selectbox(
            "Which table would you like ask questions about?",
            [table["name"] for table in base_schema["tables"]],
        )

        if "messages" not in st.session_state:
            st.session_state["messages"] = [
                # {"role": "assistant", "content": "How can I help you?"}
            ]

        for msg in st.session_state.messages:
            st.chat_message(msg["role"]).write(msg["content"])

        if prompt := st.chat_input(
            f"Enter a question about the '{table_for_ai}' table"
        ):
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.chat_message("user").write(prompt)

            with st.spinner("Generating response ..."):
                # TODO refactor, but caching is built into the connector
                df_for_ai = airtable_conn.query(
                    base_id=selected_base_id,
                    table_id=table_for_ai,
                    cell_format="string",
                    time_zone="America/Los_Angeles",
                    user_locale="en-us",
                )

                # Initiate language model
                llm = ChatOpenAIWrapper(
                    model_name="gpt-4-32k",
                    temperature=0,
                    openai_api_key=openai_api_key,
                )

                # Create Pandas DataFrame Agent
                agent = create_pandas_dataframe_agent(
                    llm,
                    df_for_ai,
                    verbose=True,
                    #agent_type=AgentType.OPENAI_FUNCTIONS,
                    number_of_head_rows=1,
                    prefix="""
                        You are working with a pandas dataframe in Python. The name of the dataframe is `df`.
                        Keep in mind that you have a limited context window.
                        This means you should avoid queries that will generate a large amount of data unless absolutely necessary.
                        For example, avoid queries that return all rows in the dataframe unless absolutely necessary.

                        Also, make sure to avoid returning code.  Ensure that you are returning real information based on the base.
                        """
                )
                # Perform Query using the Agent
                response = {"content": agent.run(prompt), "role": "assistant"}

            st.session_state.messages.append(response)
            st.chat_message("assistant").write(response["content"])
