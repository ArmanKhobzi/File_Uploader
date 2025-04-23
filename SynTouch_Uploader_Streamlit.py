import streamlit as st
import xml.etree.ElementTree as ET
import pandas as pd
import os


def extract_measurements(xml_content):
    try:
        root = ET.fromstring(xml_content)
    except ET.ParseError as e:
        st.error(f"Error parsing XML file: {e}")
        return []

    measurements = []
    for analyzer_result in root.findall('AnalyzerResult'):
        measurement = {}
        measurement['Type'] = analyzer_result.find('Type').text
        measurement['Mean'] = float(analyzer_result.find('Mean').text)
        measurement['SD'] = float(analyzer_result.find('SD').text)
        values = [float(value.text) for value in analyzer_result.findall('Values/double')]
        measurement['Values'] = values
        measurements.append(measurement)

    return measurements


def measurements_to_dataframe(measurements):
    all_rows = []
    for measurement in measurements:
        factor_type = measurement['Type']
        for value in measurement['Values']:
            all_rows.append([factor_type, value])
    df = pd.DataFrame(all_rows, columns=['Type', 'Value'])
    df = df.sort_values(by=['Type', 'Value'], key=lambda col: col.astype(str))
    return df


st.title("XML to CSV Converter")
st.markdown("Please only upload `PERCEPTS` files.")

uploaded_files = st.file_uploader("Upload XML files", type="xml", key="xml_upload", accept_multiple_files=True)

if uploaded_files:
    for uploaded_file in uploaded_files:
        xml_content = uploaded_file.getvalue().decode("utf-8")
        measurements = extract_measurements(xml_content)

        if measurements:
            df = measurements_to_dataframe(measurements)

            csv = df.to_csv(index=False).encode('utf-8')
            output_filename = os.path.splitext(uploaded_file.name)[0] + '.csv'

            st.download_button(
                label=f"Download CSV for {uploaded_file.name}",
                data=csv,
                file_name=output_filename,
                mime='text/csv',
                key=f"download_{uploaded_file.name}"
            )
        else:
            st.warning(f"No measurements found or XML parsing failed for {uploaded_file.name}.")

