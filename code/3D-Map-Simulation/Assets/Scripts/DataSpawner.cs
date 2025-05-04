using System.Collections.Generic;
using UnityEngine;

public class DataSpawner : MonoBehaviour
{
    public GameObject dataPointPrefab;

    string filename = "in";

    void Start()
    {
        SpawnData();
    }

    void SpawnData()
    {
        TextAsset textFile = Resources.Load<TextAsset>(filename); // no extension
        if (textFile == null)
        {
            Debug.LogError("Text file not found in Resources folder.");
            return;
        }

        string content = textFile.text;
        string[] split = content.Split('\n');
        List<string[]> dataList = new List<string[]>();
        for (int i = 0; i < split.Length; i++)
        {
            string[] data = split[i].Split(',');
            dataList.Add(data);
        }

        // f"{packet.lat},{packet.lon},{packet.altitude()},{packet.speed},{packet.dir_deg}\n"

        for (int i = 0; i < dataList.Count; i++)
        {
            string[] data = dataList[i];
            if (data.Length != 5)
            {
                Debug.LogError($"Data format error at line {i + 1}.");
                continue;
            }

            float lat = float.Parse(data[0]);
            float lon = float.Parse(data[1]);
            float altitude = float.Parse(data[2]);
            float speed = float.Parse(data[3]);
            float dir_deg = float.Parse(data[4]);

            GameObject dataPoint = Instantiate(dataPointPrefab);
            dataPoint.GetComponent<DataPointScript>().Init(new GeodeticCoords(lat, lon), new Altitude(altitude));
        }
    }
}
