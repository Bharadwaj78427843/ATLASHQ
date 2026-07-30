"use client";

import { useState, useCallback, useEffect } from "react";
import { OrganizationService } from "../services";
import {
  OrganizationRead,
  OrganizationList,
  OrganizationCreate,
  OrganizationUpdate,
} from "../types";
import { ApiError } from "@/lib/api";

export function useOrganizations(type: "all" | "mine" = "all") {
  const [data, setData] = useState<OrganizationList | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchOrgs = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const res = await OrganizationService.getOrganizations(type);
      setData(res);
    } catch (err) {
      setError(
        err instanceof ApiError ? err.detail : "Failed to load organizations"
      );
    } finally {
      setIsLoading(false);
    }
  }, [type]);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchOrgs();
  }, [fetchOrgs]);

  return { data, isLoading, error, refetch: fetchOrgs };
}

export function useOrganization(id: string) {
  const [data, setData] = useState<OrganizationRead | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchOrg = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const res = await OrganizationService.getOrganization(id);
      setData(res);
    } catch (err) {
      setError(
        err instanceof ApiError ? err.detail : "Failed to load organization"
      );
    } finally {
      setIsLoading(false);
    }
  }, [id]);

  useEffect(() => {
    if (id) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      fetchOrg();
    }
  }, [fetchOrg, id]);

  const update = async (payload: OrganizationUpdate) => {
    const updated = await OrganizationService.updateOrganization(id, payload);
    setData(updated);
    return updated;
  };

  const remove = async () => {
    await OrganizationService.deleteOrganization(id);
    setData(null);
  };

  return { data, isLoading, error, refetch: fetchOrg, update, remove };
}

export function useCreateOrganization() {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const create = async (payload: OrganizationCreate) => {
    setIsSubmitting(true);
    setError(null);

    try {
      const res = await OrganizationService.createOrganization(payload);
      return res;
    } catch (err) {
      const msg =
        err instanceof ApiError ? err.detail : "Failed to create organization";
      setError(msg);
      throw err;
    } finally {
      setIsSubmitting(false);
    }
  };

  return { create, isSubmitting, error, clearError: () => setError(null) };
}
