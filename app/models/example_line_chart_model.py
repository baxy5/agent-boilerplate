from typing import Any, Dict, List

from pydantic import BaseModel


class Title(BaseModel):
  text: str


class ToolboxFeature(BaseModel):
  saveAsImage: Dict[str, Any] = {}


class Toolbox(BaseModel):
  feature: ToolboxFeature


class XAxis(BaseModel):
  type: str
  data: List[str]


class YAxis(BaseModel):
  type: str


class SeriesItem(BaseModel):
  data: List[int]
  type: str


class ChartConfig(BaseModel):
  title: Title
  toolbox: Toolbox
  xAxis: XAxis
  yAxis: YAxis
  series: List[SeriesItem]
