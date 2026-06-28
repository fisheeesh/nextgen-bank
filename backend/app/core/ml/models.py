import uuid
from datetime import datetime, timezone

from sqlalchemy import text
from sqlalchemy.dialects import postgresql as pg
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Column, Field, Relationship, SQLModel

from .schema import ModelStatusEnum


class MLModel(SQLModel, table=True):
    id: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID(as_uuid=True),
            primary_key=True,
        ),
        default_factory=uuid.uuid4,
    )
    name: str = Field(index=True)
    version: str = Field(index=True)
    status: ModelStatusEnum = Field(default=ModelStatusEnum.TRAINING)
    # ? store the area under the ROC curve socre, which is measure of the models's ability to distinguish between postive and negative values
    # ? this area under roc curve, which is `AUC`, basically represents the probability that
    # ? our model is gonna rak a randmonly chosen positve instance higher than a randomly chose negative one
    auc_score: float = Field(default=0.0)
    # ? measure how often the model is correct when it predict fraud
    precision: float = Field(default=0.0)
    # ? store the recall of the model which is the raio of the true positives to all the actual postives
    recall: float = Field(default=0.0)
    # ? f1 score is the harmonic mean of the precison and the recall
    # * above 2 values provides a balance between these recall and precision
    f1_score: float = Field(default=0.0)
    features: list[str] = Field(sa_column=Column(pg.ARRAY(pg.VARCHAR)))
    # ? hyperparameters are settings that are used to train the model or control the training process of the model
    hyperparameters: dict = Field(sa_column=Column(JSONB))
    training_dataset_size: int = Field(default=0)

    mlflow_run_id: str | None = Field(default=None)
    mlflow_experiment_id: str | None = Field(default=None)
    mlflow_model_uri: str | None = Field(default=None)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            pg.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP"),
        ),
    )
    trained_at: datetime | None = Field(
        default=None,
        sa_column=Column(
            pg.TIMESTAMP(timezone=True),
            nullable=True,
        ),
    )
    deployed_at: datetime | None = Field(
        default=None,
        sa_column=Column(
            pg.TIMESTAMP(timezone=True),
            nullable=True,
        ),
    )
    predictions: list["ModelPrediction"] = Relationship(back_populates="model")


class ModelPrediction(SQLModel, table=True):
    id: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID(as_uuid=True),
            primary_key=True,
        ),
        default_factory=uuid.uuid4,
    )
    transaction_id: uuid.UUID = Field(
        foreign_key="transaction.id",
        index=True,
    )
    model_id: uuid.UUID = Field(foreign_key="mlmodel.id", index=True)
    prediction_score: float = Field(ge=0, le=1)
    prediction_timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            pg.TIMESTAMP(timezone=True),
            nullable=False,
        ),
    )
    input_features: dict = Field(sa_column=Column(JSONB))
    true_label: bool | None = Field(default=None)
    mlflow_run_id: str | None = Field(default=None)
    model: "MLModel" = Relationship(back_populates="predictions")


class TrainingDataset(SQLModel, table=True):
    id: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID(as_uuid=True),
            primary_key=True,
        ),
        default_factory=uuid.uuid4,
    )
    name: str
    version: str
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            pg.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP"),
        ),
    )
    total_samples: int
    fraud_samples: int
    legitimate_samples: int
    start_date: datetime = Field(
        sa_column=Column(
            pg.TIMESTAMP(timezone=True),
            nullable=False,
        ),
    )
    end_date: datetime = Field(
        sa_column=Column(
            pg.TIMESTAMP(timezone=True),
            nullable=False,
        ),
    )
    dataset_path: str
    mlflow_artifact_uri: str | None = Field(default=None)
    feature_info: dict = Field(sa_column=Column(JSONB))
