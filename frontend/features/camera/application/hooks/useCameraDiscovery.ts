"use client";

import { useAtom } from "jotai";
import { useCallback } from "react";
import { cameraApi } from "../../infrastructure/api/cameraApi";
import { discoveryStateAtom } from "../atoms/cameraAtoms";

export function useCameraDiscovery() {
  const [state, setState] = useAtom(discoveryStateAtom);

  const discover = useCallback(
    async (timeout = 3.0) => {
      setState({ status: "DISCOVERING" });
      try {
        const cameras = await cameraApi.discover(timeout);
        setState({ status: "DISCOVERED", cameras });
      } catch (e) {
        setState({
          status: "ERROR",
          message: e instanceof Error ? e.message : "검색 실패",
        });
      }
    },
    [setState],
  );

  const reset = useCallback(() => {
    setState({ status: "IDLE" });
  }, [setState]);

  return { state, discover, reset };
}
