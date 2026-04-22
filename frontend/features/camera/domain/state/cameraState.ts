import type { Camera, DiscoveredCamera } from "../model/camera";

export type CameraListState =
  | { status: "IDLE" }
  | { status: "LOADING" }
  | { status: "LOADED"; cameras: Camera[] }
  | { status: "ERROR"; message: string };

export type DiscoveryState =
  | { status: "IDLE" }
  | { status: "DISCOVERING" }
  | { status: "DISCOVERED"; cameras: DiscoveredCamera[] }
  | { status: "ERROR"; message: string };
