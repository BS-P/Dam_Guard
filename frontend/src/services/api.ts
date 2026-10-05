import axios from 'axios';
import { Project, Dataset, Scenario, SimulationRun, Measurement, Annotation, SolverStatus, HealthStatus } from '../types';

const API_BASE_URL = (import.meta as any).env?.VITE_API_URL || '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const apiService = {
  // System Health & Solvers
  getHealth: async (): Promise<HealthStatus> => {
    const res = await api.get('/health');
    return res.data;
  },

  getSolverStatuses: async (): Promise<SolverStatus[]> => {
    try {
      const res = await api.get('/solvers');
      return res.data;
    } catch {
      const res = await api.get('/health/solvers');
      return res.data;
    }
  },

  // Projects
  getProjects: async (): Promise<Project[]> => {
    const res = await api.get('/projects');
    return res.data;
  },

  getProject: async (id: string): Promise<Project> => {
    const res = await api.get(`/projects/${id}`);
    return res.data;
  },

  createProject: async (data: Partial<Project>): Promise<Project> => {
    const res = await api.post('/projects', data);
    return res.data;
  },

  deleteProject: async (id: string): Promise<void> => {
    await api.delete(`/projects/${id}`);
  },

  // Datasets
  getDatasets: async (projectId: string): Promise<Dataset[]> => {
    const res = await api.get(`/projects/${projectId}/datasets`);
    return res.data;
  },

  // Scenarios
  getScenarios: async (projectId: string): Promise<Scenario[]> => {
    const res = await api.get(`/projects/${projectId}/scenarios`);
    return res.data;
  },

  createScenario: async (projectId: string, data: any): Promise<Scenario> => {
    const res = await api.post(`/projects/${projectId}/scenarios`, data);
    return res.data;
  },

  // Breach Outflow Computation
  computeBreach: async (projectId: string, data: any): Promise<any> => {
    try {
      const pid = projectId || 'proj-machhu-1979';
      const res = await api.post(`/projects/${pid}/breach/compute`, data);
      return res.data;
    } catch {
      const res = await api.post('/projects/breach/compute', data);
      return res.data;
    }
  },

  // Simulation Runs
  getRuns: async (projectId: string): Promise<SimulationRun[]> => {
    const res = await api.get(`/projects/${projectId}/runs`);
    return res.data;
  },

  getRunStatus: async (projectId: string, runId: string): Promise<SimulationRun> => {
    const res = await api.get(`/projects/${projectId}/runs/${runId}`);
    return res.data;
  },

  startRun: async (projectId: string, scenarioId: string, data: any): Promise<any> => {
    const res = await api.post(`/projects/${projectId}/scenarios/${scenarioId}/runs`, data);
    return res.data;
  },

  cancelRun: async (projectId: string, runId: string): Promise<void> => {
    await api.delete(`/projects/${projectId}/runs/${runId}`);
  },

  // Measurements
  getMeasurements: async (projectId: string): Promise<Measurement[]> => {
    const res = await api.get(`/projects/${projectId}/measurements`);
    return res.data;
  },

  createMeasurement: async (projectId: string, data: any): Promise<Measurement> => {
    const res = await api.post(`/projects/${projectId}/measurements`, data);
    return res.data;
  },

  deleteMeasurement: async (projectId: string, measurementId: string): Promise<void> => {
    await api.delete(`/projects/${projectId}/measurements/${measurementId}`);
  },

  // Annotations
  getAnnotations: async (projectId: string): Promise<Annotation[]> => {
    const res = await api.get(`/projects/${projectId}/annotations`);
    return res.data;
  },

  createAnnotation: async (projectId: string, data: any): Promise<Annotation> => {
    const res = await api.post(`/projects/${projectId}/annotations`, data);
    return res.data;
  },

  deleteAnnotation: async (projectId: string, annotationId: string): Promise<void> => {
    await api.delete(`/projects/${projectId}/annotations/${annotationId}`);
  },

  // Exports
  triggerExport: async (projectId: string, runId: string, format: string): Promise<any> => {
    const res = await api.post(`/projects/${projectId}/runs/${runId}/export`, { format });
    return res.data;
  }
};
