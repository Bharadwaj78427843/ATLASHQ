"use client";

import { useState, useCallback, useEffect } from "react";
import { OrganizationService } from "../services";
import {
  OrganizationRead,
  OrganizationList,
  OrganizationCreate,
  OrganizationUpdate,
} from "../types";
import { getAccessToken } from "@/lib/auth";
import { ApiError } from "@/lib/api";

export function useOrganizations(type: "all" | "mine" = "all") {
  const [data, setData] = useState<OrganizationList | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchOrgs = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    const token = getAccessToken();
    if (!token) {
      setError("Not authenticated");
      setIsLoading(false);
      return;
    }

    try {
      const res = await OrganizationService.getOrganizations(token, type);
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
    const token = getAccessToken();
    if (!token) {
      setError("Not authenticated");
      setIsLoading(false);
      return;
    }

    try {
      const res = await OrganizationService.getOrganization(token, id);
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
    if (id) fetchOrg();
  }, [fetchOrg, id]);

  const update = async (payload: OrganizationUpdate) => {
    const token = getAccessToken();
    if (!token) throw new Error("Not authenticated");
    const updated = await OrganizationService.updateOrganization(token, id, payload);
    setData(updated);
    return updated;
  };

  const remove = async () => {
    const token = getAccessToken();
    if (!token) throw new Error("Not authenticated");
    await OrganizationService.deleteOrganization(token, id);
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
    const token = getAccessToken();
    if (!token) {
      setError("Not authenticated");
      setIsSubmitting(false);
      throw new Error("Not authenticated");
    }

    try {
      const res = await OrganizationService.createOrganization(token, payload);
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
