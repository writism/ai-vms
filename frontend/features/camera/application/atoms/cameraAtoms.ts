import { atom } from "jotai";
import type { CameraListState, DiscoveryState } from "../../domain/state/cameraState";

export const cameraListStateAtom = atom<CameraListState>({ status: "IDLE" });
export const discoveryStateAtom = atom<DiscoveryState>({ status: "IDLE" });
