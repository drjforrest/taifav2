'use client'

import { useState, useEffect } from 'react'
import { apiClient, API_ENDPOINTS } from '@/lib/api-client'
export type { PublicationFilters } from "@/types/api"
import { Publication, PublicationFilters, PublicationStats } from '@/types/api'

export interface PublicationsResult {
  publications: Publication[]
  total: number
  loading: boolean
  error: string | null
}

export function usePublications(filters: PublicationFilters = {}): PublicationsResult {
  const [publications, setPublications] = useState<Publication[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchPublications()
  }, [
    filters.search,
    filters.domain,
    filters.source,
    filters.year,
    filters.minAfricanScore,
    filters.minAiScore,
    filters.limit,
    filters.offset
  ])

  const fetchPublications = async () => {
    try {
      setLoading(true)
      setError(null)

      // Build query parameters
      const queryParams = new URLSearchParams()
      
      if (filters.search) queryParams.append('search', filters.search)
      if (filters.domain) queryParams.append('domain', filters.domain)
      if (filters.source) queryParams.append('source', filters.source)
      if (filters.year) queryParams.append('year', filters.year.toString())
      if (filters.minAfricanScore !== undefined) {
        queryParams.append('minAfricanScore', filters.minAfricanScore.toString())
      }
      if (filters.minAiScore !== undefined) {
        queryParams.append('minAiScore', filters.minAiScore.toString())
      }
      if (filters.limit) queryParams.append('limit', filters.limit.toString())
      if (filters.offset) queryParams.append('offset', filters.offset.toString())

      const url = `${API_ENDPOINTS.publications.list}?${queryParams.toString()}`
      const response = await apiClient.get<{
        publications: Publication[]
        total: number
      }>(url)

      setPublications(response.publications || [])
      setTotal(response.total || 0)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch publications')
      console.error('Error fetching publications:', err)
    } finally {
      setLoading(false)
    }
  }

  return { publications, total, loading, error }
}

// Hook for getting publication statistics
export function usePublicationStats() {
  const [stats, setStats] = useState<PublicationStats & {
    loading: boolean
    error: string | null
  }>({
    totalPublications: 0,
    bySource: {},
    byYear: {},
    byDomain: {},
    avgAfricanScore: 0,
    avgAiScore: 0,
    loading: true,
    error: null
  })

  useEffect(() => {
    fetchStats()
  }, [])

  const fetchStats = async () => {
    try {
      const statsData = await apiClient.get<PublicationStats>(
        API_ENDPOINTS.publications.stats
      )

      setStats({
        ...statsData,
        loading: false,
        error: null
      })
    } catch (err) {
      setStats(prev => ({
        ...prev,
        loading: false,
        error: err instanceof Error ? err.message : 'Failed to fetch stats'
      }))
      console.error('Error fetching publication stats:', err)
    }
  }

  return stats
}
