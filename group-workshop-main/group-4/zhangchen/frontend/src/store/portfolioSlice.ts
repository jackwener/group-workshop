import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { portfolioApi } from '../services/api';
import type { PortfolioOverview, HoldingWithFund } from '../types';

interface PortfolioState {
  overview: PortfolioOverview | null;
  holdings: HoldingWithFund[];
  loading: boolean;
  error: string | null;
}

const initialState: PortfolioState = {
  overview: null,
  holdings: [],
  loading: false,
  error: null,
};

export const fetchPortfolioOverview = createAsyncThunk(
  'portfolio/fetchOverview',
  async (contestId: number, { rejectWithValue }) => {
    try {
      const response = await portfolioApi.getOverview(contestId);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || '获取投资组合失败');
    }
  }
);

export const fetchHoldings = createAsyncThunk(
  'portfolio/fetchHoldings',
  async (contestId: number, { rejectWithValue }) => {
    try {
      const response = await portfolioApi.getHoldings(contestId);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || '获取持仓失败');
    }
  }
);

const portfolioSlice = createSlice({
  name: 'portfolio',
  initialState,
  reducers: {
    clearPortfolio: (state) => {
      state.overview = null;
      state.holdings = [];
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch Overview
      .addCase(fetchPortfolioOverview.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchPortfolioOverview.fulfilled, (state, action: PayloadAction<PortfolioOverview>) => {
        state.loading = false;
        state.overview = action.payload;
      })
      .addCase(fetchPortfolioOverview.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      // Fetch Holdings
      .addCase(fetchHoldings.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchHoldings.fulfilled, (state, action: PayloadAction<HoldingWithFund[]>) => {
        state.loading = false;
        state.holdings = action.payload;
      })
      .addCase(fetchHoldings.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });
  },
});

export const { clearPortfolio } = portfolioSlice.actions;
export default portfolioSlice.reducer;
