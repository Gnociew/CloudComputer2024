# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
from pathlib import Path

import gin
import numpy as np
import numpy.typing as npt
import tensorflow as tf
import faiss
from modules import utils

from . import augmentation, model


@gin.configurable
class TranslatorManager():

    def __init__(self, model_path: str, labels: dict, faiss_index_path: str, n_frames: int) -> None:
        self.n_frames = n_frames
        self.softmax_labels = labels
        self.faiss_index_path = Path(faiss_index_path)

        self.model = model.get_model()
        self.model.load_weights(model_path)
        self.model = tf.function(self.model)

        self.faiss_index = None  # Faiss 索引对象
        self.knn_labels = []  # 索引中每个向量对应的标签

    def load_knn_database(self):
        """
        加载 Faiss 索引和对应的标签。
        """
        logging.info("Loading Faiss index...")
        if not self.faiss_index_path.is_file():
            logging.error(f"Faiss index file not found at {self.faiss_index_path}")
            return False

        # 加载 Faiss 索引
        self.faiss_index = faiss.read_index(str(self.faiss_index_path))
        logging.info(f"Loaded Faiss index with {self.faiss_index.ntotal} vectors.")

        # 加载对应的标签
        label_path = self.faiss_index_path.with_suffix(".labels.npy")
        if not label_path.is_file():
            logging.error(f"Labels file not found at {label_path}")
            return False

        self.knn_labels = np.load(label_path)
        logging.info(f"Loaded {len(self.knn_labels)} labels.")
        return True

    def save_knn_database(self, gloss_name, knn_records):
        new_labels = [gloss_name] * len(knn_records)
        new_data=np.array(knn_records)
        logging.info("Saving new data to Faiss index...")

        # 如果索引不存在，需要重新创建
        if self.faiss_index is None:
            dimension = new_data.shape[1]
            self.faiss_index = faiss.IndexFlatL2(dimension)

        # 添加新数据到索引
        self.faiss_index.add(new_data)
        logging.info(f"Added {len(new_data)} vectors to Faiss index.")

        # 更新标签
        if len(self.knn_labels) == 0:
            self.knn_labels = np.array(new_labels)
        else:
            self.knn_labels = np.concatenate([self.knn_labels, new_labels])

        # 保存标签文件
        np.save(self.faiss_index_path.with_suffix(".labels"), self.knn_labels)
        logging.info("Labels updated and saved.")

        # 保存索引文件
        faiss.write_index(self.faiss_index, str(self.faiss_index_path))
        logging.info(f"Faiss index saved to {self.faiss_index_path}.")

    def preprocess_input(self, vid_res: dict, resampling: int):
        # Remove non-visible joints.
        vid_res = utils.skeleton_utils.filter_visibility(vid_res)
        if resampling > 0:
            indices = utils.skeleton_utils.uniform_sampling(vid_res["n_frames"], n_pick=resampling)
            vid_res["n_frames"] = resampling
            vid_res = utils.skeleton_utils.apply_resampling(vid_res, indices)

        return vid_res

    def get_feats(self, vid_res: dict, is_augment=False):
        vid_res = self.preprocess_input(vid_res, self.n_frames)

        if is_augment:
            vid_res = augmentation.augment_video(vid_res)

        feats_out, cls_out = self.model([
            vid_res["pose_frames"][np.newaxis], vid_res["face_frames"][np.newaxis], vid_res["lh_frames"][np.newaxis],
            vid_res["rh_frames"][np.newaxis]
        ])
        return feats_out.numpy().squeeze()

    def run_knn(self, feats: npt.ArrayLike, k=5):
        """
        使用 Faiss 索引进行最近邻查询。
        """
        if self.faiss_index is None:
            logging.error("Faiss index not loaded. Call load_knn_database() first.")
            return None

        # 查询最近邻
        feats = np.expand_dims(feats, axis=0).astype('float32')  # 确保查询向量是二维的
        distances, indices = self.faiss_index.search(feats, k)

        # 获取最近邻的标签
        top_labels = self.knn_labels[indices[0]]

        # 统计最近邻中出现次数最多的标签
        vals, counts = np.unique(top_labels, return_counts=True)
        index = np.argmax(counts)
        res_txt = vals[index]

        return res_txt
