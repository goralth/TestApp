import { useEffect, useRef } from "react";
import Map from "@arcgis/core/Map";
import MapView from "@arcgis/core/views/MapView";
import FeatureLayer from "@arcgis/core/layers/FeatureLayer";

type Props = {
  statesVisible: boolean;
  countiesVisible: boolean;
  citiesVisible: boolean;
};

type Stats = {
  pop_count: number;
  pop_sum: number;
  pop_avg: number;
  pop_min: number;
  pop_max: number;
};

export default function MapViewComponent({
  statesVisible,
  countiesVisible,
  citiesVisible,
}: Props) {
  const mapDivRef = useRef<HTMLDivElement | null>(null);
  const statesLayerRef = useRef<FeatureLayer | null>(null);
  const countiesLayerRef = useRef<FeatureLayer | null>(null);
  const citiesLayerRef = useRef<FeatureLayer | null>(null);

  useEffect(() => {
    const statesLayer = new FeatureLayer({
      url: "https://sampleserver6.arcgisonline.com/arcgis/rest/services/Census/MapServer/3",
      title: "USA States",
      opacity: 0.35,
    });

    const countiesLayer = new FeatureLayer({
      url: "https://sampleserver6.arcgisonline.com/arcgis/rest/services/Census/MapServer/2",
      title: "USA Counties",
      opacity: 0.2,
    });

    const citiesLayer = new FeatureLayer({
      url: "https://sampleserver6.arcgisonline.com/arcgis/rest/services/SampleWorldCities/MapServer/0",
      title: "World Cities",
    });

    statesLayerRef.current = statesLayer;
    countiesLayerRef.current = countiesLayer;
    citiesLayerRef.current = citiesLayer;

    const map = new Map({
      basemap: "gray-vector",
      layers: [countiesLayer, statesLayer, citiesLayer],
    });

    const view = new MapView({
      container: mapDivRef.current as HTMLDivElement,
      map,
      center: [-98.5795, 39.8283],
      zoom: 4,
    });

    const resetMap = () => {
      view.goTo({ center: [-98.5795, 39.8283], zoom: 4 });
    };

    const analyzePOP2000 = async (layer: FeatureLayer): Promise<Stats> => {
      await layer.load();
      const query = layer.createQuery();
      query.where = "1=1";
      query.returnGeometry = false;
      query.outStatistics = [
        { statisticType: "count", onStatisticField: "POP2000", outStatisticFieldName: "pop_count" },
        { statisticType: "sum", onStatisticField: "POP2000", outStatisticFieldName: "pop_sum" },
        { statisticType: "avg", onStatisticField: "POP2000", outStatisticFieldName: "pop_avg" },
        { statisticType: "min", onStatisticField: "POP2000", outStatisticFieldName: "pop_min" },
        { statisticType: "max", onStatisticField: "POP2000", outStatisticFieldName: "pop_max" },
      ];

      const result = await layer.queryFeatures(query);
      return result.features[0].attributes as Stats;
    };

    (window as Window & typeof globalThis & {
      resetMap?: () => void;
      analyzePOP2000?: (layerName: string) => Promise<Stats>;
      getPOP2000Stats?: (layerName: string) => Promise<Stats>;
    }).resetMap = resetMap;

    (window as Window & typeof globalThis & {
      analyzePOP2000?: (layerName: string) => Promise<Stats>;
      getPOP2000Stats?: (layerName: string) => Promise<Stats>;
    }).analyzePOP2000 = async (layerName: string) => {
      if (layerName === "states") return analyzePOP2000(statesLayer);
      if (layerName === "counties") return analyzePOP2000(countiesLayer);
      throw new Error("Unknown layer");
    };

    (window as Window & typeof globalThis & {
      getPOP2000Stats?: (layerName: string) => Promise<Stats>;
    }).getPOP2000Stats = async (layerName: string) => {
      const analyze = (window as any).analyzePOP2000;
      return analyze(layerName);
    };

    return () => {
      view.destroy();
      (window as any).resetMap = undefined;
      (window as any).analyzePOP2000 = undefined;
      (window as any).getPOP2000Stats = undefined;
    };
  }, []);

  useEffect(() => {
    if (statesLayerRef.current) statesLayerRef.current.visible = statesVisible;
  }, [statesVisible]);

  useEffect(() => {
    if (countiesLayerRef.current) countiesLayerRef.current.visible = countiesVisible;
  }, [countiesVisible]);

  useEffect(() => {
    if (citiesLayerRef.current) citiesLayerRef.current.visible = citiesVisible;
  }, [citiesVisible]);

  return <div ref={mapDivRef} id="viewDiv" style={{ width: "100%", height: "100vh" }} />;
}